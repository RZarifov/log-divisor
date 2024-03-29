import os
import re
import textwrap
from datetime import datetime
from logging import getLogger
from collections import defaultdict
from enum import Flag, auto


logger = getLogger(__name__)


class WISENESS(Flag):
    """
    THE WISENESS FLAG
    A convenient way to represent one of seven possible states of operation.
    Y stands for a Year;
    M stands for a Month;
    D stands for a Day.

    The idea behind this lies within the desire to parse the single log file
    in one pass, yet splitting only in required specification.
    For example when we need to split the log file only yearly and daily,
    skipping monthly split. For this particular example we just use
    an object that represents WISENESS.YD
    """
    Y = auto()
    M = auto()
    D = auto()
    YM = Y | M
    YD = Y | D
    MD = M | D
    YMD = Y | M | D


class DATE_FORMAT:
    """
    Date formats representation.
    If a user wants to supply different formats for the log,
    he must instance this class.

    The default formats are:
        date_re = r'(\d+-\d+-\d+ \d+:\d+:\d+)'
            used in matching the log date in log entry
        date_strp = '%Y-%m-%d %H:%M:%S'
            used in datetime date management.
    """
    def __init__(self, date_strp = '%Y-%m-%d %H:%M:%S',
            date_re = r'(\d+-\d+-\d+ \d+:\d+:\d+)'):
        self.strp = date_strp
        self.re = re.compile(date_re)


class LogDivisor(object):
    """
    Log Divisor Class.
    Provides a functionality to split large log files into more usable
    log chunks, each representing a single year, month, day, respectively.

    The instance of the class must be supplied with the path to a log file.
    Also there is an optional \"save folder path\" argument.

    The methods are:
        divide_log_file             -   The default method.
            The purpose is to split a large log file into smaller log files,
            yearly, monthly and daily-wise.

        divide_year_and_month_wise  -   Works about the same as the default
            method, yet skips splitting a provided log into daily logs.

        divide_year_and_day_wise    -   Works about the same as the default
            method, yet skips splitting a provided log into monthly logs.

        divide_month_and_day_wise   -   Works about the same as the default
            method, yet skips splitting a provided log into yearly logs.

        divide_year_wise            -   Split provided log file into smaller
            logs, each for the individual year represented in the provided log.

        divide_month_wise           -   Split provided log file into smaller
            logs, each for the individual month represented in the provided log,
            under the respective year the month belongs to.

        divide_day_wise             -   Split the provided log file into smaller
            logs, each for the individual day represented in the provided log,
            under the respective year and month the day belongs to.
    """
    date_frm = DATE_FORMAT()

    def __init__(self, log_file_path,
            save_folder_path = None,
            custom_formats = None):
        """
        save_folder_path = provide a custom folder to save split logs into.
        custom_date_formats = provide custom date formats.
            Must be an instance of DATE_FORMAT.
        """
        if custom_formats:
            self.date_frm = custom_formats

        self.log_file_path = log_file_path
        self.filename, _ = os.path.splitext(log_file_path)
        self.log_subfiles = defaultdict(str)
        self.save_folder_path = save_folder_path

        try:
            self.log_file = open(self.log_file_path, "r")
        except OSError as exception:
            log_message = textwrap.dedent(f"""\
                The program experienced an error: {exception.strerror},
                While trying to open the file \"{self.log_file_path}\".
                {"="*80}""")

            logger.error(log_message, exc_info=True)
            exit(1)
        except Exception as exception:
            logger.error(f"Unknown exception occurred: {exc.strerror}", 
                exc_info=True)
            exit(1)

    def _get_subfile_name(self, line, wiseness):
        match = self.date_frm.re.search(line)
        if match:
            matchDate = match.group(1)
            try:
                dt = datetime.strptime(matchDate, self.date_frm.strp)
            except ValueError:
                return self._get_corrupt_entries_file_path()

            base_name = self._get_base_name(dt, wiseness)

            if self.save_folder_path:
                subfile_name = f"{self.save_folder_path}/{base_name}.log"
            else:
                if os.path.isfile(self.filename):
                    subfile_name = f"{self.filename}_divided/{base_name}.log"
                else:
                    subfile_name = f"{self.filename}/{base_name}.log"

            return subfile_name
        else:
            return self._get_corrupt_entries_file_path()

    def _get_base_name(self, dt, wiseness):
        if wiseness == WISENESS.Y:
            base_name = f"{dt.year}"
        elif wiseness == WISENESS.M:
            base_name = f"{dt.year}/{dt.strftime('%b')}"
        elif wiseness == WISENESS.D:
            base_name = f"{dt.year}/{dt.strftime('%b')}/{dt.day:02d}"
        else:
            raise ValueError("Wrong wiseness value. Expected either Y, M, D.")

        return base_name

    def _get_corrupt_entries_file_path(self):
        if self.save_folder_path:
            subfile_name = f"{self.save_folder_path}/corrupt_log_entries.log"
        else:
            if os.path.isfile(self.filename):
                subfile_name = f"{self.filename}_divided/corrupt_log_entries.log"
            else:
                subfile_name = f"{self.filename}/corrupt_log_entries.log"
        
        return subfile_name

    def _check_directory(_, subfile_name):
        folder_name = os.path.split(subfile_name)[0]

        try:
            if not os.path.isdir(folder_name):
                os.makedirs(folder_name)
        except OSError:
            log_message = textwrap.dedent(f"""\
                The program experienced an error: {exception.strerror},
                While trying to make directories \"{folder_name}\".
                {"="*80}""")

            logger.error(log_message, exc_info=True)
            exit(1)
        except Exception as exception:
            logger.error(f"Unknown exception occurred: {exc.strerror}", 
                exc_info=True)
            exit(1)

    def _divide_file(self, wiseness):
        for line in self.log_file:
            files_to_write = set()
            if wiseness & WISENESS.Y == WISENESS.Y:
                files_to_write.add(self._get_subfile_name(line, WISENESS.Y))
            if wiseness & WISENESS.M == WISENESS.M:
                files_to_write.add(self._get_subfile_name(line, WISENESS.M))
            if wiseness & WISENESS.D == WISENESS.D:
                files_to_write.add(self._get_subfile_name(line, WISENESS.D))

            self._write_to_sublog_files(files_to_write, line)

        else:
            self.log_file.seek(0)

            for key, file in list(self.log_subfiles.items()):
                file.close()
                self.log_subfiles.pop(key)

    def _write_to_sublog_files(self, files_to_write, line):
        for subfile_name in files_to_write:
            self._check_directory(subfile_name)
            if not self.log_subfiles[subfile_name]:
                self.log_subfiles[subfile_name] = open(subfile_name, "w+")

            self.log_subfiles[subfile_name].write(line)

    def divide_log_file(self, save_folder_path = None):
        """
        The default method.
        The purpose is to split a large log file into smaller log files,
        yearly, monthly and daily-wise.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.YMD)

    def divide_year_and_month_wise(self, save_folder_path = None):
        """
        Works about the same as the default method,
        yet skips splitting a provided log into daily logs.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.YM)

    def divide_year_and_day_wise(self, save_folder_path = None):
        """
        Works about the same as the default method,
        yet skips splitting a provided log into monthly logs.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.YD)

    def divide_month_and_day_wise(self, save_folder_path = None):
        """
        Works about the same as the default method,
        yet skips splitting a provided log into yearly logs.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.MD)

    def divide_year_wise(self, save_folder_path = None):
        """
        Split provided log file into smaller logs,
        each for the individual year represented in the provided log.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.Y)

    def divide_month_wise(self, save_folder_path = None):
        """
        Split provided log file into smaller logs,
        each for the individual month represented in the provided log,
        under the respective year the month belongs to.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.M)

    def divide_day_wise(self, save_folder_path = None):
        """
        Split the provided log file into smaller logs,
        each for the individual day represented in the provided log,
        under the respective year and month the day belongs to.
        """
        if save_folder_path:
            self.save_folder_path = save_folder_path
        self._divide_file(WISENESS.D)


if __name__ == "__main__":
    ld = LogDivisor("test_files/one_line.log", save_folder_path="D:/olo/trololo")
    ld.divide_log_file()
