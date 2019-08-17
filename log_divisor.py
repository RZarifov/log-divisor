import os
import re
import textwrap
from datetime import datetime
from logging import getLogger
from collections import defaultdict


logger = getLogger(__name__)


class LogDivisor(object):
    date_re = re.compile(r'(\d+-\d+-\d+ \d+:\d+:\d+)')

    def __init__(self, log_file_name, 
            save_folder_path = None,
            date_format_re = None):
        if date_format_re:
            self.date_re = date_format_re

        self.log_file_name = log_file_name
        self.log_subfiles = defaultdict(str)
        self.save_folder_path = save_folder_path

        try:
            self.log_file = open(self.log_file_name, "r")
        except OSError as exception:
            log_message = textwrap.dedent(f"""\
                The program experienced an error: {exception.strerror},
                While trying to open the file \"{self.log_file_name}\".
                {"="*80}""")

            logger.error(log_message, exc_info=True)
            exit(1)
        except Exception as exception:
            logger.error(f"Unknown exception occurred: {exc.strerror}", 
                exc_info=True)

    def _get_subfile_name(self, line, yearly):
        match = self.date_re.search(line)
        if match:
            matchDate = match.group(1)
            dt = datetime.strptime(matchDate, '%Y-%m-%d %H:%M:%S')

            if yearly:
                base_name = f"{dt.year}"
            else:
                base_name = f"{dt.year}/{dt.strftime('%b')}"

            filename, _ = os.path.splitext(self.log_file.name)
            if self.save_folder_path:
                subfile_name = f"{self.provided_path}/{dt.year}.log"
            else:
                if os.path.isfile(filename):
                    subfile_name = f"{filename}_divided/{base_name}.log"
                else:
                    subfile_name = f"{filename}/{base_name}.log"
        else:
            if self.save_folder_path:
                subfile_name = f"{self.provided_path}/corrupt_log_entries.log"
            else:
                if os.path.isfile(filename):
                    subfile_name = f"{filename}_divided/corrupt_log_entries.log"
                else:
                    subfile_name = f"{filename}/corrupt_log_entries.log"
        return subfile_name

    def _check_directory(_, subfile_name):
        folder_name = os.path.split(subfile_name)[0]

        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

    def divide_log_file(self):
        self.divide_year_wise()
        self.divide_month_wise()

    def divide_year_wise(self):
        self._divide_file(yearly = True)

    def divide_month_wise(self):
        self._divide_file(yearly = False)

    def _divide_file(self, yearly = True):
        for line in self.log_file:
            subfile_name = self._get_subfile_name(line, yearly)

            self._check_directory(subfile_name)
            if not self.log_subfiles[subfile_name]:
                self.log_subfiles[subfile_name] = open(subfile_name, "w+")

            self.log_subfiles[subfile_name].write(line)
        else:
            self.log_file.seek(0)

            for key, file in list(self.log_subfiles.items()):
                file.close()
                self.log_subfiles.pop(key)


def get_new_log_subfile(name, year=None, month=None):
    if year:
        return open(f'{name}/{year}')


if __name__ == '__main__':
    ld = LogDivisor('test_files/sample_large.log')
    ld.divide_log_file()
