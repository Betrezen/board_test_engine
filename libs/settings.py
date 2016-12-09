import os
import socket

from log import logger, set_file

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'settings.conf')

##############################
# common #
##############################
REPO_ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_REPORT_FOLDER = os.path.join(REPO_ROOT_FOLDER, '.reports')
PATH_TO_CPYTHON27 = os.environ.get('PATH_TO_CPYTHON27', 'C:\Python27')
LOG_FILENAME = os.path.join(REPO_ROOT_FOLDER, 'results.log')

##############################
# Logging #
##############################
set_file(LOG_FILENAME)
LOGGER = logger
# logger.debug("LOG_FILENAME={}".format(LOG_FILENAME))
# logger.debug("REPO_ROOT_FOLDER={}".format(REPO_ROOT_FOLDER))
# logger.debug("TEST_REPORT_FOLDER={}".format(TEST_REPORT_FOLDER))

##############################
# Ports #
##############################
FTDI1_SERIAL_PORT = 'COM101'
FTDI2_SERIAL_PORT = 'COM102'
FTDI3_SERIAL_PORT = 'COM103'
HID_SERAIL_PORT = 'COM104'

##############################
# Services #
##############################
DBFILE = 'board_test_results.db'
DBPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DBFILE)
print "DBPATH={}".format(DBPATH)

ZEROMQ_SERVER_HOST = socket.gethostbyname(socket.gethostname())
ZEROMQ_SERVER_PORT = 9595

##############################
# Test report fields #
##############################
BOARD_TEST_NAME =             'board_test_name'
BOARD_TEST_STEPS =            'board_test_steps'
BOARD_TEST_EXPECTED_RESULTS = 'board_test_expected_results'
BOARD_TEST_SUITE_NAME =       'board_test_suite_name'
BOARD_TEST_ACTUAL_VALUE =     'board_test_actual_value'
BOARD_TEST_PROGRESS =         'board_test_progress'
BOARD_TEST_REPORT_PATH =      'board_test_report_path'
BOARD_TEST_STARTED =          'STARTED'
BOARD_TEST_COMPLETED =        'COMPLETED'

BOARD_TEST_RESULT =        'board_test_result'
BOARD_TEST_RESULT_VALUES = ['PASS', 'FAIL']
BOARD_TEST_RESULT_PASS =   'PASS'
BOARD_TEST_RESULT_FAIL =   'FAIL'

BOARD_TEST_SESS_PROGRESS =     'board_test_session_progress'
BOARD_TEST_SESS_TOTAL_TCS =    'board_test_session_total_tcs'
BOARD_TEST_SESS_TOTAL_FAILED = 'board_test_session_total_failed'
BOARD_TEST_SESS_STARTED =      'STARTED'
BOARD_TEST_SESS_FINISHED =     'COMPLETED'
BOARD_TEST_SESS_RESULT =       'board_test_session_result'
BOARD_TEST_SESS_RESULT_PASS =  'PASS'
BOARD_TEST_SESS_RESULT_FAIL =  'FAIL'

##############################
# Flask #
##############################
FLASK_SESSION_TYPE = 'filesystem'
FLASK_UPLOAD_FOLDER = './static/storage'
FLASK_ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
FLASK_RESOURCE_STATUSES = ['OK', 'NOK', 'NA', 'XZ']
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DBFILE)

logger.debug("FLASK_SESSION_TYPE={}".format(FLASK_SESSION_TYPE))
logger.debug("FLASK_UPLOAD_FOLDER={}".format(FLASK_UPLOAD_FOLDER))
logger.debug("FLASK_ALLOWED_EXTENSIONS={}".format(FLASK_ALLOWED_EXTENSIONS))
logger.debug("FLASK_RESOURCE_STATUSES={}".format(FLASK_RESOURCE_STATUSES))
