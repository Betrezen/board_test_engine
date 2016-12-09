"""
--------------------------
Actions for mail window
--------------------------
"""
import json
import os
import sys
import time
from multiprocessing import Process, Queue
from xml.etree import ElementTree
import webbrowser

from PySide import QtCore, QtGui
import waiting

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)

from qt_client.draw import Draw
from qt_client.qtmain import Ui_MainWindow
from test_engine.base import BaseOperations
from libs.db import DbProxy
from libs.subscriber import ZMQSubscriber
from libs.settings import LOGGER
from libs.settings import (
    BOARD_TEST_ACTUAL_VALUE, BOARD_TEST_COMPLETED, BOARD_TEST_EXPECTED_RESULTS,
    BOARD_TEST_NAME, BOARD_TEST_PROGRESS, BOARD_TEST_REPORT_PATH,
    BOARD_TEST_RESULT, BOARD_TEST_RESULT_FAIL, BOARD_TEST_SESS_FINISHED,
    BOARD_TEST_SESS_PROGRESS, BOARD_TEST_SESS_RESULT,
    BOARD_TEST_SESS_RESULT_FAIL, BOARD_TEST_SESS_RESULT_PASS,
    BOARD_TEST_SESS_STARTED, BOARD_TEST_SESS_TOTAL_TCS,
    BOARD_TEST_STARTED, TEST_REPORT_FOLDER, REPO_ROOT_FOLDER)


SHORT_SLEEP_TIME = 0.2
FILE_WAIT_TIME = 10
DB_RECORDS_DISPLAY_LIMIT = 25

DB_XML_RESULT_EXTRACTION_FILE = 'report_for_display.xml'
BOARD_IMG_FILE = os.path.join(REPO_ROOT_FOLDER, 'images', 'board.png')
BOARD_IMG_FILE_SN = os.path.join(REPO_ROOT_FOLDER, 'images', 'sn.png')

TESTS_TOTAL_RESULTS_MSG = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd"><html>'
    '<body style="font-style:normal; background-color: {backgr};">'
    '<p align="center">'
    '<span style="font-size:20pt; font-weight:600; '
    'color:{color};">{status}'
    '</span></p></body></html>')


def init_test_engine():
    """Run PyTest tests"""
    base = BaseOperations()
    base.run_pytest_tests()


class HelpersFunctions(object):
    """Some useful functions"""

    @staticmethod
    def xml_read_from_file(test_report_path, delete=True):
        """Read xml from file

        :param test_report_path: (str) Full path to xml file
        :param delete: (bool) Delete file after read?
        :return: (str) String with parsed xml file content
        :raises: TimeoutExpired if file still not present after timeout
        """
        try:
            waiting.wait(
                lambda: os.path.isfile(test_report_path) is True,
                sleep_seconds=1,
                timeout_seconds=FILE_WAIT_TIME)
        except waiting.TimeoutExpired as e:
            # TODO(akoryag): Need to do something with this exception
            raise e

        tree = ElementTree.parse(test_report_path)
        root = tree.getroot()
        xml_rep = ElementTree.tostring(root, encoding='utf8', method='xml')
        if delete:
            os.remove(test_report_path)
        return xml_rep

    @staticmethod
    def xml_read_from_db(raw_xml_str):
        """Convert raw XML-dump string to XML element

        :param raw_xml_str: (str) Raw xml text string extracted from DB
        :return: xml.etree.ElementTree.ElementTree object
        """
        raw_xml_str = raw_xml_str.encode('utf8')
        raw_xml_str = raw_xml_str.decode('string_escape')[1:-1:]
        xml_elem = ElementTree.fromstring(raw_xml_str)
        xml_tree = ElementTree.ElementTree(xml_elem)
        return xml_tree

    @staticmethod
    def xml_write_to_file(xml_tree_obj, file_path):
        """Write provided XML object to provided file

        :param xml_tree_obj: (object) xml.etree.ElementTree.ElementTree
        :param file_path: (str) Full path to xml file
        :return: None
        """
        xml_tree_obj.write(file_path)


class QueueSubscribe(QtCore.QThread, HelpersFunctions):
    """Class to run in separate thread"""

    pb_setvalue = QtCore.Signal(int, name="pb_setValue")
    pb_reset = QtCore.Signal(name="pb_reset")
    set_sess_result = QtCore.Signal(dict, name="set_sess_result")
    table_autoresizecolumn = QtCore.Signal(int, name="table_resizeColumn")
    drawNotes = QtCore.Signal(str, name="test_name")

    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

        self.test_log_table = parent.test_log_table
        self.progress_bar = parent.progress_bar
        self.test_table = parent.test_table
        self.barcode_input = parent.barcode_input
        self.test_btn = parent.test_btn
        self.sess_results = parent.sess_results

        self.dbproxy = parent.dbproxy
        self.disable_input = parent.disable_input
        self.stop_test_engine = parent.stop_test_engine

        self.test_engine = None

        self.subscriber_queue = Queue()
        self.subscriber = ZMQSubscriber(self.subscriber_queue)

        self.pb_num_of_tcs = None

    def run(self):
        """This will be run on thread start"""
        while self.exiting is False:
            self.catch_test_session()
        self.stop_subscriber()
        self.stop_db()

    def catch_test_session(self):
        """Catch messages related to test execution"""

        def _get_message():
            """Read message from queue"""
            raw_msg = self.subscriber_queue.get()
            return json.loads(raw_msg[raw_msg.find('{'):])

        def _save_results_to_db():
            """Save results to DataBase"""
            self.add_to_db(message)
            time.sleep(SHORT_SLEEP_TIME)

        def _session_passed():
            """Actions if test session was PASSED"""
            self.pb_setvalue.emit(self.pb_num_of_tcs)
            self.set_sess_result.emit(
                {'status': '- PASS -', 'backgr': 'green'})
            self.barcode_input.setFocus()

        def _session_failed():
            """Actions if test session was FAILED"""
            self.pb_reset.emit()
            self.test_log_table.addItem("! Session FAILED !")
            self.set_sess_result.emit({'status': '- FAIL -', 'backgr': 'red'})
            self.barcode_input.setFocus()

        def _session_started():
            """Actions when test session has STARTED"""
            msg = "-- Tests have been started -------"
            self.test_log_table.addItem(msg)

            self.pb_num_of_tcs = int(message.get(BOARD_TEST_SESS_TOTAL_TCS))
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(self.pb_num_of_tcs)
            self.pb_setvalue.emit(0)
            self.test_log_table.addItem(str(message))

            self.set_sess_result.emit({'status': 'Running', 'backgr': 'white'})

        def _session_completed():
            """Actions when test session has COMPLETED"""
            self.test_log_table.addItem(str(message))
            self.stop_test_engine()

            msg = ("-- Tests were completed -------\nStatus is: {}\n"
                   "".format(message.get(BOARD_TEST_SESS_RESULT)))
            self.test_log_table.addItem(msg)

            _save_results_to_db()

            if message.get(
                    BOARD_TEST_SESS_RESULT) == BOARD_TEST_SESS_RESULT_PASS:
                _session_passed()
            elif message.get(
                    BOARD_TEST_SESS_RESULT) == BOARD_TEST_SESS_RESULT_FAIL:
                _session_failed()

            self.disable_input(False)

        if not self.subscriber_queue.empty():
            message = _get_message()
            LOGGER.debug("DO_SUBSCRIBE: message=%s", message)

            if message.get(
                    BOARD_TEST_SESS_PROGRESS) == BOARD_TEST_SESS_STARTED:
                _session_started()

            elif message.get(
                    BOARD_TEST_SESS_PROGRESS) == BOARD_TEST_SESS_FINISHED:
                _session_completed()

            else:
                self.put_results_in_gui(message)
                self.test_log_table.addItem(str(message))
                time.sleep(SHORT_SLEEP_TIME)
        else:
            # no messages
            time.sleep(SHORT_SLEEP_TIME)

    def put_results_in_gui(self, message):
        """Put results in Window GUI"""

        def _put_in_table():
            """Put results in GUI in table"""
            results = {
                'name': message.get(BOARD_TEST_NAME),
                'result': message.get(BOARD_TEST_RESULT, '. . .'),
                'actual': message.get(BOARD_TEST_ACTUAL_VALUE, '. . .'),
                'expected': message.get(BOARD_TEST_EXPECTED_RESULTS)}

            row_ind = self.test_table.rowCount()

            # Rewrite row if it has same test name
            if (row_ind > 0 and self.test_table.item(row_ind - 1, 0).
                    text() == results['name']):
                row_ind -= 1
            else:
                self.test_table.insertRow(row_ind)

            item = QtGui.QTableWidgetItem
            self.test_table.setItem(row_ind, 0, item(str(results['name'])))
            self.test_table.setItem(row_ind, 1, item(str(results['result'])))
            self.test_table.setItem(row_ind, 2, item(str(results['actual'])))
            self.test_table.setItem(row_ind, 3, item(str(results['expected'])))

            _resize_columns_to_contents([0, 1, 2])

            if results['result'] == BOARD_TEST_RESULT_FAIL:
                self.test_table.item(row_ind, 1).setBackground(
                    QtGui.QColor('red'))

        def _resize_columns_to_contents(columns):
            """resizeColumnToContents"""
            for i in columns:
                self.table_autoresizecolumn.emit(i)

        def _test_started():
            """Actions when ONE test has STARTED"""
            _put_in_table()
            test_name = message.get(BOARD_TEST_NAME, None)
            if test_name:
                self.drawNotes.emit(test_name)

        def _test_completed():
            """Actions when ONE test has COMPLETED"""
            _put_in_table()
            self.pb_setvalue.emit(self.progress_bar.value() + 1)
            print "\nRES={}".format(message)

        if message.get(BOARD_TEST_PROGRESS, None) == BOARD_TEST_STARTED:
            _test_started()
        elif message.get(BOARD_TEST_PROGRESS, None) == BOARD_TEST_COMPLETED:
            _test_completed()
        else:
            pass

    def add_to_db(self, message):
        """Add results to DB"""
        test_report_path = message.get(BOARD_TEST_REPORT_PATH)
        xml_rep = self.xml_read_from_file(test_report_path)

        status = message.get(
            BOARD_TEST_SESS_RESULT) == BOARD_TEST_SESS_RESULT_PASS
        self.dbproxy.add_result(
            barcode=self.barcode_input.text(),
            status=status,
            result=xml_rep)

    def stop_subscriber(self):
        """Stop ZMQ subscriber"""
        self.subscriber.stop()

    def stop_db(self):
        """Stop DB"""
        self.dbproxy.close_session()

    def clear_queue(self):
        """Clear ZMQ message queue"""
        while not self.subscriber_queue.empty():
            self.subscriber_queue.get(block=True)


class ControlMainWindow(QtGui.QMainWindow, HelpersFunctions):
    """Main window"""

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.draw = Draw()
        # self.showMaximized()

        self.tab_widget = self.ui.tabWidget
        self.db_results_table = self.ui.dbresultsTableWidget
        self.db_sync_btn = self.ui.dbsyncPushButton
        self.test_btn = self.ui.testButton
        self.stop_btn = self.ui.stopButton
        self.stop_btn.setDisabled(True)
        self.test_log_table = self.ui.testLogTable
        self.test_table = self.ui.testTable
        self.barcode_input = self.ui.barcodeLineEdit
        self.barcode_input.setFocus()
        self.graphics_view = self.ui.graphicsView
        self.progress_bar = self.ui.progressBar
        self.limit_to_label = self.ui.limitToLabel
        self.limit_to_label.setText(
            'Results limited to {0} last records from DB'.format(
                DB_RECORDS_DISPLAY_LIMIT))
        self.sess_results = self.ui.totalresults_text
        self.set_sess_status({'status': 'Not Started', 'color': 'grey'})

        self.db_sync_btn.clicked.connect(self.sync2db)
        self.test_btn.clicked.connect(self.start_tests)
        self.stop_btn.clicked.connect(self.stop_test_engine)
        self.barcode_input.returnPressed.connect(self.start_tests)
        self.connect(self.tab_widget, QtCore.SIGNAL('currentChanged(int)'),
                     self.tab_open)
        app.aboutToQuit.connect(self.do_close)

        # Add board image
        scene = QtGui.QGraphicsScene()
        self.board_image = QtGui.QPixmap(BOARD_IMG_FILE)
        item = QtGui.QGraphicsPixmapItem(self.board_image)
        scene.addItem(item)
        self.ui.graphicsView.setScene(scene)

        self.ui.graphicsView.resizeEvent = self.gv_resize
        QtCore.QObject.connect(self.ui.graphicsView, QtCore.SIGNAL('resize()'),
                               self.gv_resize)

        # Only for help in graphic notes design
        self.ui.graphicsView.mouseMoveEvent = self.gv_mmovie
        QtCore.QObject.connect(
            self.ui.graphicsView, QtCore.SIGNAL('mouseMoveEvent()'),
            self.gv_mmovie)
        self.ui.graphicsView.mouseDoubleClickEvent = self.gv_clear
        QtCore.QObject.connect(
            self.ui.graphicsView, QtCore.SIGNAL('mouseDoubleClickEvent()'),
            self.gv_clear)

        self.test_engine = None
        self.dbproxy = DbProxy()

        # Run test session messages listening
        self.subscriber_receive_thread = QueueSubscribe(self)
        self.subscriber_receive_thread.start()
        self.subscriber_receive_thread.pb_setvalue.connect(
            self.progress_bar.setValue)
        self.subscriber_receive_thread.pb_reset.connect(
            self.progress_bar.reset)
        self.subscriber_receive_thread.table_autoresizecolumn.connect(
            self.test_table.resizeColumnToContents)
        self.subscriber_receive_thread.drawNotes.connect(self.draw_notes)
        self.subscriber_receive_thread.set_sess_result.connect(
            self.set_sess_status)

        self.test_log_table.clear()

    def set_sess_status(self, kwargs):
        """Set HTML text in text browser window

        :param kwargs: Like:
            {'status': '- PASS -', 'color': 'green', 'backgr': 'white'}
        """
        status = kwargs.get('status', 'no status')
        color = kwargs.get('color', 'black')
        backgr = kwargs.get('backgr', 'white')
        self.sess_results.setHtml(
            TESTS_TOTAL_RESULTS_MSG.format(
                status=status, color=color, backgr=backgr))

    def tab_open(self, selected_index):
        """Actions when tab switched"""
        if selected_index == 1:
            self.sync2db()

    def gv_mmovie(self, event):
        """Show coordinates
        Only for help in graphic notes design
        """
        scenePt = self.ui.graphicsView.mapToScene(event.pos())
        scene_x = round(scenePt.x())
        scene_y = round(scenePt.y())
        self.setWindowTitle(str(scene_x) + ", " + str(scene_y))

    def gv_clear(self):
        """Remove graphic items from scene"""
        for i in self.ui.graphicsView.scene().items():
            if i.type() != 7:
                self.ui.graphicsView.scene().removeItem(i)
        print "----"
        # self.ui.graphicsView.repaint()

    def draw_notes(self, test_name):
        """Draw lines and text on board image"""
        self.gv_clear()
        scene = self.ui.graphicsView.scene()

        if test_name == 'test_00_check_sn1':
            self.ui.graphicsView.scene().clear()
            self.board_image = QtGui.QPixmap(BOARD_IMG_FILE_SN)
            item = QtGui.QGraphicsPixmapItem(self.board_image)
            scene.addItem(item)

        elif test_name == 'test_01_measure_vpsu_to_gnd':
            self.ui.graphicsView.scene().clear()
            self.board_image = QtGui.QPixmap(BOARD_IMG_FILE)
            item = QtGui.QGraphicsPixmapItem(self.board_image)
            scene.addItem(item)

        else:
            # TODO(akoryag): Just to show possibilities
            import random
            points = self.draw.points_info.keys()
            self.draw.draw_point_and_line(scene, random.choice(points))

    def gv_resize(self, event):
        """Resize image"""
        self.ui.graphicsView.fitInView(
            self.ui.graphicsView.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def sync2db(self):
        """Extract information from DB and put it in Window"""

        def _view_button_clicked():
            """Extract xml report from DB, save if as s file, open it"""
            xml_file = os.path.join(TEST_REPORT_FOLDER,
                                    DB_XML_RESULT_EXTRACTION_FILE)

            button = QtGui.qApp.focusWidget()
            index = self.db_results_table.indexAt(button.pos())
            if index.isValid():
                date = self.db_results_table.item(
                    index.row(), index.column() - 2).text()
                report = self.dbproxy.get_report_by_date(date)
                report = self.xml_read_from_db(report)
                self.xml_write_to_file(report, xml_file)
                webbrowser.open(xml_file)

        records = self.dbproxy.get_all(limit=DB_RECORDS_DISPLAY_LIMIT)
        if records:
            for n, i in enumerate(records):
                if self.db_results_table.rowCount() <= n:
                    self.db_results_table.insertRow(n)
                item_barcode = QtGui.QTableWidgetItem(str(i.barcode))
                item_date = QtGui.QTableWidgetItem(str(i.date_time))
                item_status = QtGui.QTableWidgetItem(str(i.status))

                self.db_results_table.setItem(n, 0, item_barcode)
                self.db_results_table.setItem(n, 1, item_date)
                self.db_results_table.setItem(n, 2, item_status)

                cell_view_btn = QtGui.QPushButton('View report')
                cell_view_btn.clicked.connect(_view_button_clicked)
                self.db_results_table.setCellWidget(n, 3, cell_view_btn)

        LOGGER.debug("COUNT_ROWS = %s", self.db_results_table.rowCount())

    def retest_barcode_if_not_unique(self, barcode):
        """What to do if barcode already present in DB"""
        if self.dbproxy.is_barcode_present(barcode):
            print 'Barcode already presents in DB'
            choice = QtGui.QMessageBox.question(
                self,
                self.tr("Barcode already presents in database."),
                self.tr("Barcode '{0}' already presents in database.\n\n"
                        "Delete previous results and re-test this board?"
                        "".format(barcode)),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.Yes)

            if choice == QtGui.QMessageBox.No:
                return False
            elif choice == QtGui.QMessageBox.Yes:
                return True
        else:
            print 'Barcode is unique'
            return True

    def disable_input(self, disable=True):
        """Input buttons/text areas disable/enable"""
        self.test_btn.setDisabled(disable)
        self.barcode_input.setDisabled(disable)
        self.stop_btn.setDisabled(not disable)

    def do_clear(self):
        """Clear tables in GUI"""
        self.setStyleSheet('')
        self.test_log_table.clear()
        self.test_table.setRowCount(0)
        self.subscriber_receive_thread.clear_queue()

    def start_tests(self):
        """Start tests"""
        self.do_clear()
        self.disable_input(True)

        barcode = self.barcode_input.text()

        test_barcode = self.retest_barcode_if_not_unique(barcode)
        if test_barcode is True:
            self.dbproxy.delete_record_by_barcode(barcode)
            self.test_log_table.addItem("barcode={}".format(barcode))
            self.test_engine = Process(target=init_test_engine, args=())
            self.test_engine.start()
            self.subscriber_receive_thread.test_engine = self.test_engine

        elif test_barcode is False:
            self.disable_input(False)
            self.test_log_table.addItem(
                'Tests for board with barcode "{}" were skipped.'
                ''.format(barcode))
        else:
            self.disable_input(False)
            self.test_log_table.addItem('????')

    def stop_test_engine(self):
        """Terminate process with test engine"""
        LOGGER.debug("TEST_ENGINE process are going to be terminated.")
        if self.test_engine and self.test_engine.is_alive():
            self.test_engine.terminate()
            self.test_engine = None
        self.test_log_table.addItem('- TEST ENGINE STOPPED -')
        # Enable input buttons
        self.disable_input(False)

    def do_close(self):
        """Actions before closing main window"""
        print "DO_CLOSE"
        self.subscriber_receive_thread.exiting = True
        self.stop_test_engine()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
