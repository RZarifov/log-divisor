# The Log divisor #
__Description:__\
A library for analyzing and splitting the large log file into smaller, manageable chunks, for respective year, month, day.

__Dependencies:__\
None

__Usage:__
```python
from log_divisor improt LogDivisor as LD
ld = LD("path_to_log/file.log")
ld.divide_log_file("path_to_save_the_split_logs") # argument is optional.
# By default it outputs the split files next to the processed log file.
```

__Supported formats:__\
The default, and only format for this version is '%Y-%m-%d %H:%M:%S'
If the user wants to process the log file in different format, he should instance the DATE_FORMAT,
by providing both time format and the regex format. The arguments for the instance are: time_strp and date_regex respectively
The The default representation of both is:
```python
date_regex = r'(\d+-\d+-\d+ \d+:\d+:\d+)',
time_strp = '%Y-%m-%d %H:%M:%S'
```

*Possible future enhancement*: Guessing the regex format from the time_strp format, freeing the user from the necessity to provide one.

__TODOs:__
* TODO: Get rid of the custom regex format, deduce it from the time format
* TODO: Support async code and operations
* TODO: Multiple formats support out of the box
* TODO: pypi release
