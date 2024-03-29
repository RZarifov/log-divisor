import unittest

import os
import shutil

from log_divisor import LogDivisor, WISENESS


class UnusedTestCases(unittest.TestCase):
    """
    The unused test cases. They supposed to mock the file reading and writing
    operations, removing the need to work with the actual files.
    The idea behind these test cases abandoned due to the time constraints.
    """
    def _test_open(self):
        m = unittest.mock.mock_open()
        with unittest.mock.patch('tests.open', m):
            with open('foo', 'w') as h:
                h.write('some stuff')

        m.assert_called_once_with('foo', 'w')
        handle = m()
        handle.write.assert_called_once_with('some stuff')

    def _test_read(self):
        with unittest.mock.patch('tests.open',
                unittest.mock.mock_open(read_data='bibble')) as m:
            with open('foo') as h:
                result = h.read()
        m.assert_called_once_with('foo')
        assert result == 'bibble'

    def _test_opening_file(self):
        log_line = "2018-01-01 19:49:16: many example match now clean rock favor interest sister three"

        with unittest.mock.patch('log_divisor.open',
                unittest.mock.mock_open(read_data=log_line)) as m:
            ld = LogDivisor('log_file.log')
        m.assert_called_once_with('log_file.log', 'r')

    def _test_writing_to_split_files(self):
        m = unittest.mock.mock_open()
        with unittest.mock.patch('log_divisor.open', m):
            ld = LogDivisor('log_file.log')
            ld.divide_year_wise()
            #with open('foo', 'w') as h:
            #    h.write('some stuff')

        m.assert_called_with('log_file.log', 'r')
        handle = m()
        #handle.write.assert_called_once_with('some stuff')


class BasicLogTests(unittest.TestCase):
    """
    The test cases to test WISENESS Flag attribute,
    as well as basic one line log file.
    """
    def test_ymd_wiseness(self):
        wiseness = WISENESS.YMD
        self.assertTrue(wiseness & WISENESS.Y == WISENESS.Y)
        self.assertTrue(wiseness & WISENESS.M == WISENESS.M)
        self.assertTrue(wiseness & WISENESS.D == WISENESS.D)

    def test_ym_wiseness(self):
        wiseness = WISENESS.YM
        self.assertTrue(wiseness & WISENESS.Y == WISENESS.Y)
        self.assertTrue(wiseness & WISENESS.M == WISENESS.M)
        self.assertFalse(wiseness & WISENESS.D == WISENESS.D)

    def test_yd_wiseness(self):
        wiseness = WISENESS.YD
        self.assertTrue(wiseness & WISENESS.Y == WISENESS.Y)
        self.assertFalse(wiseness & WISENESS.M == WISENESS.M)
        self.assertTrue(wiseness & WISENESS.D == WISENESS.D)

    def test_m_wiseness(self):
        wiseness = WISENESS.M
        self.assertFalse(wiseness & WISENESS.Y == WISENESS.Y)
        self.assertTrue(wiseness & WISENESS.M == WISENESS.M)
        self.assertFalse(wiseness & WISENESS.D == WISENESS.D)

    def test_writing_an_actual_log(self):
        test_file = "test_files/one_line.log"
        test_file_folder, _ = os.path.splitext(test_file)

        output_yearly_file = os.path.join(test_file_folder, "2018.log")
        output_monthly_file = os.path.join(test_file_folder, "2018/Jan.log")
        output_daily_file = os.path.join(test_file_folder, "2018/Jan/01.log")

        log_line = "2018-01-01 19:49:16: many example match now clean rock favor interest sister three"

        try:
            ld = LogDivisor(test_file)
            ld.divide_log_file()

            with open(output_yearly_file, 'r') as f:
                yearly_text = f.read()

            with open(output_monthly_file, 'r') as f:
                monthly_text = f.read()

            with open(output_daily_file, 'r') as f:
                daily_text = f.read()
        finally:
            shutil.rmtree(test_file_folder)
        
        self.assertEqual(log_line, yearly_text)
        self.assertEqual(log_line, monthly_text)
        self.assertEqual(log_line, daily_text)
