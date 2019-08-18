import os
import re
import textwrap
from datetime import datetime
from logging import getLogger
from collections import defaultdict
from enum import Flag, auto


class WISENESS(Flag):
    Y = auto()
    M = auto()
    D = auto()
    YM = Y | M
    YD = Y | D
    MD = M | D
    YMD = Y | M | D


logger = getLogger(__name__)


class LogDivisor(object):
    date_re = re.compile(r'(\d+-\d+-\d+ \d+:\d+:\d+)')

    def __init__(self, log_file_path, 
            save_folder_path = None,
            date_format_re = None):
        if date_format_re:
            self.date_re = date_format_re

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
        match = self.date_re.search(line)
        if match:
            matchDate = match.group(1)
            try:
                dt = datetime.strptime(matchDate, '%Y-%m-%d %H:%M:%S')
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
            if wiseness & WISENESS.Y == WISENESS.Y:
                subfile_name = self._get_subfile_name(line, WISENESS.Y)
                self._write_to_sublog_file(subfile_name, line)
            if wiseness & WISENESS.M == WISENESS.M:
                subfile_name = self._get_subfile_name(line, WISENESS.M)
                self._write_to_sublog_file(subfile_name, line)
            if wiseness & WISENESS.D == WISENESS.D:
                subfile_name = self._get_subfile_name(line, WISENESS.D)
                self._write_to_sublog_file(subfile_name, line)
        else:
            self.log_file.seek(0)

            for key, file in list(self.log_subfiles.items()):
                file.close()
                self.log_subfiles.pop(key)

    def _write_to_sublog_file(self, subfile_name, line):
        self._check_directory(subfile_name)
        if not self.log_subfiles[subfile_name]:
            self.log_subfiles[subfile_name] = open(subfile_name, "w+")

        self.log_subfiles[subfile_name].write(line)

    def divide_log_file(self):
        self._divide_file(WISENESS.YMD)

    def divide_year_and_month_wise(self):
        self._divide_file(WISENESS.YM)

    def divide_year_and_day_wise(self):
        self._divide_file(WISENESS.YD)

    def divide_month_and_day_wise(self):
        self._divide_file(WISENESS.MD)

    def divide_year_wise(self):
        self._divide_file(WISENESS.Y)

    def divide_month_wise(self):
        self._divide_file(WISENESS.M)

    def divide_day_wise(self):
        self._divide_file(WISENESS.D)


if __name__ == "__main__":
    ld = LogDivisor("test_files/sample_large.log", save_folder_path="olo/trololo")
    ld.divide_day_wise()
