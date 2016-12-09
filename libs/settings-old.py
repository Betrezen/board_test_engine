# -*- python -*-
# author: krozin@gmail.com
# settings: created 2016/10/30.
# copyright

import os
import socket

from log import logger, set_file
from yamlloader import get_env

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'settings.conf')
env = get_env(filepath=filepath,  attrdict=True)

##############################
# common #
##############################
TEST_ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_REPORT_FOLDER = os.path.join(TEST_ROOT_FOLDER, 'Reports')
try:
    PATH_TO_CPYTHON27 = env.common.PATH_TO_CPYTHON27
except:
    PATH_TO_CPYTHON27 = os.environ.get('PATH_TO_CPYTHON27', 'C:\Python27')

try:
    LOG_FILENAME = env.common.LOG_FILENAME
except:
    LOG_FILENAME = os.path.join(TEST_ROOT_FOLDER, 'results.log')

try:
    TEST_REPORT_FOLDER = env.common.TEST_REPORT_FOLDER
except:
    TEST_REPORT_FOLDER = os.path.join(TEST_ROOT_FOLDER, 'Reports')

##############################
# Logging #
##############################
set_file(LOG_FILENAME)
LOGGER = logger
#logger.debug("LOG_FILENAME={}".format(LOG_FILENAME))
#logger.debug("REPO_ROOT_FOLDER={}".format(REPO_ROOT_FOLDER))
#logger.debug("TEST_REPORT_FOLDER={}".format(TEST_REPORT_FOLDER))


##############################
# Ports #
##############################
try:
    FTDI1_SERIAL_PORT = env.interfaces.FTDI1_SERIAL_PORT
    FTDI2_SERIAL_PORT = env.interfaces.FTDI2_SERIAL_PORT
    FTDI3_SERIAL_PORT = env.interfaces.FTDI3_SERIAL_PORT
    HID_SERAIL_PORT = env.interfaces.HID_SERAIL_PORT
except:
    FTDI1_SERIAL_PORT = 'COM101'
    FTDI2_SERIAL_PORT = 'COM102'
    FTDI3_SERIAL_PORT = 'COM103'
    HID_SERAIL_PORT = 'COM104'

##############################
# Services #
##############################
try:
    DBFILE = env.db.get('filename')
    DBPATH = env.db.get('filepath')
except:
    DBFILE = 'board_test_results.db'
    DBPATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DBFILE)
print "DBPATH={}".format(DBPATH)

try:
    ZEROMQ_SERVER_HOST = env.zeromq_server.get('host')
    ZEROMQ_SERVER_PORT = int(env.zeromq_server.get('port'))
except:
    ZEROMQ_SERVER_HOST = socket.gethostname()
    ZEROMQ_SERVER_PORT = 9595

##############################
# Test report fields #
##############################
try:
    BOARD_TEST_NAME = env.testkeys.test_name
    BOARD_TEST_STEPS = env.testkeys.test_steps
    BOARD_TEST_EXPECTED_RESULTS = env.testkeys.test_expected_results
    BOARD_TEST_SUITE_NAME = env.testkeys.test_suite_name
    BOARD_TEST_ACTUAL_VALUE = env.testkeys.test_actual_value
    BOARD_TEST_PROGRESS = env.testkeys.test_progress
    BOARD_TEST_REPORT_PATH = env.testkeys.test_report_path
    BOARD_TEST_START = env.testkeys.test_start
    BOARD_TEST_FINISH = env.testkeys.test_finish
except:
    BOARD_TEST_NAME = 'board_test_name'
    BOARD_TEST_STEPS = 'board_test_steps'
    BOARD_TEST_EXPECTED_RESULTS = 'board_test_expected_results'
    BOARD_TEST_SUITE_NAME = 'board_test_suite_name'
    BOARD_TEST_ACTUAL_VALUE = 'board_test_actual_value'
    BOARD_TEST_PROGRESS = 'board_test_progress'
    BOARD_TEST_REPORT_PATH = 'board_test_report_path'
    BOARD_TEST_START = 'STARTED'
    BOARD_TEST_FINISH = 'COMPLETED'

try:
    BOARD_TEST_RESULT = env.testkeys.result
    BOARD_TEST_RESULT_VALUES = env.testkeys.result_values
    BOARD_TEST_RESULT_PASS = env.testkeys.result_pass
    BOARD_TEST_RESULT_FAIL = env.testkeys.result_fail
except:
    BOARD_TEST_RESULT = 'board_test_result'
    BOARD_TEST_RESULT_VALUES = ['PASS', 'FAIL']
    BOARD_TEST_RESULT_PASS = 'PASS'
    BOARD_TEST_RESULT_FAIL = 'FAIL'

try:
    BOARD_TEST_SESSION_STATUS = env.testkeys.test_session_status
    BOARD_TEST_SESSION_TOTAL_TCS = env.testkeys.test_session_total_tcs
    BOARD_TEST_SESSION_TOTAL_FAILED = env.testkeys.test_session_total_failed
    BOARD_TEST_SESSION_STARTED = env.testkeys.test_session_start
    BOARD_TEST_SESSION_FINISHED = env.testkeys.test_session_finish
    BOARD_TEST_SESSION_RESULT = env.testkeys.test_session_result
    BOARD_TEST_SESSION_RESULT_PASS = env.testkeys.test_session_pass
    BOARD_TEST_SESSION_RESULT_FAIL = env.testkeys.test_session_fail
except:
    BOARD_TEST_SESSION_STATUS = 'board_test_session_status'
    BOARD_TEST_SESSION_TOTAL_TCS = 'board_test_session_total_tcs'
    BOARD_TEST_SESSION_TOTAL_FAILED = 'board_test_session_total_failed'
    BOARD_TEST_SESSION_STARTED = 'STARTED'
    BOARD_TEST_SESSION_FINISHED = 'COMPLETED'
    BOARD_TEST_SESSION_RESULT = 'board_test_session_result'
    BOARD_TEST_SESSION_RESULT_PASS = 'PASS'
    BOARD_TEST_SESSION_RESULT_FAIL = 'FAIL'

##############################
# Flask #
##############################
try:
    FLASK_SESSION_TYPE = env.flask.get('session_type')
    FLASK_UPLOAD_FOLDER = env.flask.get('upload_folder')
    FLASK_ALLOWED_EXTENSIONS = env.flask.get('allowed_extensions')
    FLASK_RESOURCE_STATUSES = env.flask.get('statuses')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DBPATH)
except:
    FLASK_SESSION_TYPE = 'filesystem'
    FLASK_UPLOAD_FOLDER = './static/storage'
    FLASK_ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
    FLASK_RESOURCE_STATUSES = ['OK', 'NOK', 'NA', 'XZ']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DBFILE)

logger.debug("FLASK_SESSION_TYPE={}".format(FLASK_SESSION_TYPE))
logger.debug("FLASK_UPLOAD_FOLDER={}".format(FLASK_UPLOAD_FOLDER))
logger.debug("FLASK_ALLOWED_EXTENSIONS={}".format(FLASK_ALLOWED_EXTENSIONS))
logger.debug("FLASK_RESOURCE_STATUSES={}".format(FLASK_RESOURCE_STATUSES))
