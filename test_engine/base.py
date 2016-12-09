import os
import time

import pytest


class HWBoardEmulator(object):

    def __init__(self):
        self.SN = 123456789

        self.VPSU_TO_GND_v = 0.0
        self.VPSU_17v = 17.0
        self.TP7_v = 4.07
        self.TP1_v = 4.07
        self.TP6_v = 1.8
        self.TP2_v = 4.07
        self.TP3_v = 4.07
        self.VPSU_5v = 5.0
        self.is_17v_psu_enabled = False
        self.is_5v_psu_enabled = False
        self.is_485_2wire_mode_enabled = False

    def reset_ADC(self):
        return True

    def enable_17v_psu(self):
        self.is_17v_psu_enabled = True

    def enable_5v_psu(self):
        self.is_5v_psu_enabled = True

    def enable_485_2wire_node(self):
        self.is_485_2wire_mode_enabled = True


class BaseOperations(object):

    def get_base_dir(self):
        """Get full path to repository directory"""
        dir_of_this_file = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(dir_of_this_file)

    def run_pytest_tests(self):
        """Run pytest from Python code

        :return: (str) Full path to generated xml report
        """
        folder_with_tests = 'test_engine'
        report_folder = '.reports'
        repo_path = self.get_base_dir()
        path_to_tests = os.path.join(repo_path, folder_with_tests)

        # Like: 2016_10_31_-_13-46-29 // Year_month_day_-_24H-min-sec
        time_format = time.strftime('%Y_%m_%d_-_%H-%M-%S',  time.gmtime())
        xml_report_name = 'junit_report_{}.xml'.format(time_format)
        path_to_report = os.path.join(repo_path, report_folder, xml_report_name)

        args = [
            '-q',
            # '-v',
            '--exitfirst',
            '{folder_with_tests}'.format(folder_with_tests=path_to_tests),
            '--junitxml',
            '{report}'.format(report=path_to_report)
        ]
        pytest.main(args)

        return path_to_report

if __name__ == "__main__":
    base = BaseOperations()
    base.run_pytest_tests()
