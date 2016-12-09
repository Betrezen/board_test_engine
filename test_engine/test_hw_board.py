"""
Tests for board
"""

import json
import time

import pytest

from test_engine.base import HWBoardEmulator
from libs.settings import (
    BOARD_TEST_SESS_PROGRESS, BOARD_TEST_SESS_STARTED,
    BOARD_TEST_SESS_FINISHED, BOARD_TEST_SESS_TOTAL_TCS,
    BOARD_TEST_SESS_TOTAL_FAILED, BOARD_TEST_REPORT_PATH,
    BOARD_TEST_SESS_RESULT, BOARD_TEST_SESS_RESULT_PASS,
    BOARD_TEST_SESS_RESULT_FAIL)


class TestHWBoardFunctions(object):
    """Helpers for tests"""

    HW = HWBoardEmulator()

    @staticmethod
    def raise_error(err_msg='FAILED'):
        """Perform actions in case if test will be failed"""
        # 'FAILED' or 'LOG FAULT' or 'NOTIFY OPERATOR'
        # Do something with this error
        raise AssertionError(err_msg)

    @staticmethod
    def calculate_deviation_range(value, percentage):
        """Prepare range of numbers for possible deviation

        :param value: (int|float) Expected value
        :param percentage: (int|float) Possible +- deviation in percents
        :return: dict

        Example:
            expected_value = 17.0
            percentage     = 5
                17.0 +- 5% ==> {'min': 16.15, 'max': 17.85}
        """
        value = float(value)
        percentage = float(percentage)
        min_possible = value - (value * percentage / 100)
        max_possible = value + (value * percentage / 100)
        min_possible = round(min_possible, 3)
        max_possible = round(max_possible, 3)
        return {'min': min_possible,
                'max': max_possible}

    def check_value_in_expected_deviation(
            self, expected_value, actual_value, deviation_perc=0):
        """Check that provided value is in range of possible deviation

        :param expected_value: (int) Expected value with no deviation.
        :param actual_value: (int) Measured value
        :param deviation_perc: (int) Possible +- deviation in percents
        :return: True if in range
                 AssertionError if not in range

        Example:
            expected_value    = 17.0
            actual_value      = 16.86
            ok_deviation_perc = 5
                17 +- 5% ==> 16.15 .. 17.85
                This is True: 16.15 < 17.0 < 17.85
        """
        deviation_range = self.calculate_deviation_range(
            expected_value, deviation_perc)
        min_possible = deviation_range['min']
        max_possible = deviation_range['max']

        if not min_possible < actual_value < max_possible:
            self.raise_error(
                err_msg='Actual value "{0}" is not in range of +-{1}% from '
                        'expected value "{2}" ({3} .. {4}).'.format(
                            actual_value, deviation_perc, expected_value,
                            min_possible, max_possible))
        else:
            print 'OK: {0} less then {1} less then {2}'.format(
                min_possible, actual_value, max_possible)
            return True


class TestHWBoard(TestHWBoardFunctions):
    """PyTest Tests"""

    @pytest.fixture(scope='session', autouse=True)
    def setup(self, publisher, request):
        """Performs actions below BEFORE test execution session"""
        print 'Setup'
        to_publ = dict()
        to_publ[BOARD_TEST_SESS_PROGRESS] = BOARD_TEST_SESS_STARTED
        to_publ[BOARD_TEST_SESS_TOTAL_TCS] = request.session.testscollected
        publisher.send(receiver='all', msg=json.dumps(to_publ))

    @pytest.yield_fixture(scope='session', autouse=True)
    def teardown(self, publisher, request):
        """Performs actions below AFTER test execution session"""
        yield
        print 'Teardown'
        to_publ = dict()
        to_publ[BOARD_TEST_SESS_PROGRESS] = BOARD_TEST_SESS_FINISHED
        to_publ[BOARD_TEST_SESS_TOTAL_TCS] = request.session.testscollected
        to_publ[BOARD_TEST_SESS_TOTAL_FAILED] = request.session.testsfailed
        to_publ[BOARD_TEST_REPORT_PATH] = request.config.option.xmlpath
        if request.session.testsfailed == 0:
            to_publ[BOARD_TEST_SESS_RESULT] = BOARD_TEST_SESS_RESULT_PASS
        else:
            to_publ[BOARD_TEST_SESS_RESULT] = BOARD_TEST_SESS_RESULT_FAIL

        publisher.send(receiver='all', msg=json.dumps(to_publ))

    # -- TESTS -- Part 1 -- #

    @pytest.mark.run(order=0)
    def test_00_check_sn1(self, report_to_publisher, record_xml_property):
        """Test to check that it is possible to get SN of board.
        :Test Suite: Power control

        :Steps:
        1. Get SN of board

        :Expected Results:
        Board has SN
        -end-
        """
        sn = self.HW.SN
        record_xml_property("Serial Number", sn)
        pytest.test_actual_value = sn
        assert sn

    @pytest.mark.run(order=1)
    def test_01_measure_vpsu_to_gnd(self, report_to_publisher):
        """Test to check that VPSU to GND voltage = 0V +-1%.
        :Test Suite: Power control

        :Steps:
        1. Get actual VPSU to GND voltage
        2. Compare expected voltage with actual

        :Expected Results:
        0V +- 1%
        -end-
        """
        expected_v = 0
        real_voltage = self.HW.VPSU_TO_GND_v
        pytest.test_actual_value = real_voltage
        assert expected_v == real_voltage

    @pytest.mark.run(order=2)
    def test_02_enable_17v_psu(self, report_to_publisher):
        """Test to check that 17v PSU was enabled.
        :Test Suite: Power control

        :Steps:
        1. Check that initially 17v PSU was disabled
        2. Enable 17v PSU
        3. Check that PSU is enabled

        :Expected Results:
        PSU is enabled
        -end-
        """
        initially_enabled = self.HW.is_17v_psu_enabled
        assert initially_enabled is False

        self.HW.enable_17v_psu()
        is_enabled = self.HW.is_17v_psu_enabled
        pytest.test_actual_value = is_enabled
        assert is_enabled is True
        # import random
        # assert random.choice([True, False])

    @pytest.mark.run(order=3)
    def test_03_measure_17v_vpsu(self, report_to_publisher):
        """Test to check that VPSU voltage = 17V +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual VPSU voltage
        2. Compare expected voltage with accepted voltage deviation range.

        :Expected Results:
        17V +- 5%.
        -end-
        """
        expected_v = 17
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.VPSU_17v
        pytest.test_actual_value = actual_voltage
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=4)
    def test_04_measure_tp1(self, report_to_publisher):
        """Test to check that TP1 voltage = 4.07v +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual TP1 voltage
        2. Compare expected voltage with accepted voltage deviation range.

        :Expected Results:
        4.07V +- 5%.
        -end-
        """
        expected_v = 4.07
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.TP1_v
        pytest.test_actual_value = actual_voltage
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=5)
    def test_05_measure_tp7(self, report_to_publisher):
        """Test to check that TP7 voltage = 4.07v +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual TP7 voltage
        2. Compare expected voltage with accepted voltage deviation range.

        :Expected Results:
        4.07V +- 5%.
        -end-
        """
        expected_v = 4.07
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.TP7_v
        pytest.test_actual_value = actual_voltage
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=6)
    def test_06_measure_tp6(self, report_to_publisher):
        """Test to check that TP6 voltage = 1.8v +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Wait 4 seconds
        2. Get actual TP6 voltage
        3. Compare expected voltage with accepted voltage deviation range

        :Expected Results:
        1.8V +- 5%
        -end-
        """
        expected_v = 1.8
        possible_deviation = 5  # +- 5%
        time.sleep(4)
        actual_voltage = self.HW.TP6_v
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=7)
    def test_07_measure_tp2(self, report_to_publisher):
        """Test to check that TP2 voltage = 4.07v +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual TP2 voltage
        2. Compare expected voltage with accepted voltage deviation range

        :Expected Results:
        4.07V +- 5%
        -end-
        """
        expected_v = 4.07
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.TP2_v
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=8)
    def test_08_measure_tp3(self, report_to_publisher):
        """Test to check that TP2 voltage = 4.07v +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual TP3 voltage
        2. Compare expected voltage with accepted voltage deviation range.

        :Expected Results:
        4.07V +- 5%
        -end-
        """
        expected_v = 4.07
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.TP3_v
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=9)
    def test_09_enable_5v_psu(self, report_to_publisher):
        """Test to check that 5v PSU was enabled.
        :Test Suite: Power control

        :Steps:
        1. Check that initially 5v PSU was disabled
        2. Enable 5v PSU
        3. Check that 5v PSU is enabled

        :Expected Results:
        5v PSU enabled
        -end-
        """
        initially_enabled = self.HW.is_5v_psu_enabled
        assert initially_enabled is False

        self.HW.enable_5v_psu()
        is_enabled = self.HW.is_5v_psu_enabled
        assert is_enabled is True

    @pytest.mark.run(order=10)
    def test_10_measure_5v_vpsu(self, report_to_publisher):
        """Test to check that VPSU voltage = 5V +- 5%.
        :Test Suite: Power control

        :Steps:
        1. Get actual VPSU voltage
        2. Compare expected voltage with accepted voltage deviation range.

        :Expected Results:
        5V +- 5%
        -end-
        """
        expected_v = 5
        possible_deviation = 5  # +- 5%
        actual_voltage = self.HW.VPSU_5v
        self.check_value_in_expected_deviation(
            expected_v, actual_voltage, possible_deviation)

    @pytest.mark.run(order=11)
    def test_11_enable_485_2wire_mode(self, report_to_publisher):
        """Test to check that 485 (2-wire mode) was enabled.
        :Test Suite: Power control

        :Steps:
        1. Check that initially 485 (2-wire mode) was disabled
        2. Enable 485 (2-wire mode)
        3. Check that 485 (2-wire mode) is enabled

        :Expected Results:
        485 (2-wire mode) enabled
        -end-
        """
        initially_enabled = self.HW.is_485_2wire_mode_enabled
        assert initially_enabled is False

        self.HW.enable_485_2wire_node()
        is_enabled = self.HW.is_485_2wire_mode_enabled
        assert is_enabled is True

    # -- TESTS -- Part 2 -- #
    # Part 2 will be later...
