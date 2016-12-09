"""
Fixtures for PyTest tests
"""
import json
import re

import pytest

from libs.publisher import ZMQPublisher
from libs.settings import (
    BOARD_TEST_RESULT, BOARD_TEST_STARTED, BOARD_TEST_COMPLETED,
    BOARD_TEST_PROGRESS, BOARD_TEST_RESULT_PASS, BOARD_TEST_RESULT_FAIL,
    BOARD_TEST_NAME, BOARD_TEST_STEPS, BOARD_TEST_EXPECTED_RESULTS,
    BOARD_TEST_SUITE_NAME, BOARD_TEST_ACTUAL_VALUE)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


def pytest_namespace():
    """Namespace for exchange between different PyTest parts"""
    return {'test_actual_value': None}


@pytest.fixture(scope='session')
def publisher():
    """Connection point to ZeroMQ publisher"""
    return ZMQPublisher()


@pytest.fixture
def report_to_publisher(publisher, request):
    """Fixture to prepare and send actual test status to Publisher"""

    def find_between(start_str, end_str):
        """Find text in test's docstring between start and end line"""
        return re.findall(r'%s(.*?)%s' % (start_str, end_str),
                          test_doc_string, re.DOTALL)[0]

    def custom_strip(raw_line):
        """Delete empty lines and strip non-empty"""
        return [line.strip() for line in raw_line.split('\n') if line.strip()]

    test_suite_pattern = ':Test Suite:'
    steps_pattern = ':Steps:'
    expected_pattern = ':Expected Results:'
    end_pattern = '-end-'

    test_doc_string = request.function.__doc__

    test_suite = find_between(test_suite_pattern, steps_pattern)
    test_suite = custom_strip(test_suite)[0]

    test_steps = find_between(steps_pattern, expected_pattern)
    test_steps = custom_strip(test_steps)

    expect_result = find_between(expected_pattern, end_pattern)
    expect_result = custom_strip(expect_result)[0]

    msg_to_publ = dict()
    msg_to_publ[BOARD_TEST_NAME] = request.node.name
    msg_to_publ[BOARD_TEST_STEPS] = test_steps
    msg_to_publ[BOARD_TEST_EXPECTED_RESULTS] = expect_result
    msg_to_publ[BOARD_TEST_PROGRESS] = BOARD_TEST_STARTED
    msg_to_publ[BOARD_TEST_SUITE_NAME] = test_suite

    publisher.send(receiver='all', msg=json.dumps(msg_to_publ))
    # import time
    # time.sleep(2)
    yield
    msg_to_publ[BOARD_TEST_ACTUAL_VALUE] = pytest.test_actual_value
    msg_to_publ[BOARD_TEST_PROGRESS] = BOARD_TEST_COMPLETED

    if request.node.rep_call.failed or request.node.rep_setup.failed:
        msg_to_publ[BOARD_TEST_RESULT] = BOARD_TEST_RESULT_FAIL
        publisher.send(receiver='all', msg=json.dumps(msg_to_publ))
    else:
        msg_to_publ[BOARD_TEST_RESULT] = BOARD_TEST_RESULT_PASS
        publisher.send(receiver='all', msg=json.dumps(msg_to_publ))
