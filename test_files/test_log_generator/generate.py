import time
from random import random, choice
from configparser import RawConfigParser

from most_common_words import thousand as words


config = RawConfigParser()
config.read("config.ini")


def strf_time_prop(start, end, format, prop):
    start_time = time.mktime(time.strptime(start, format))
    end_time = time.mktime(time.strptime(end, format))
    random_time = start_time + prop * (end_time - start_time)

    return time.strftime(format, time.localtime(random_time))


def get_random_date(start, end, prop):
    return strf_time_prop(start, end, config.get('dates', 'format'), prop)


def generate_sample_log_file():
    with open("sample.log", "w+") as sample_log_file:
        log_entries = list()
        for _ in range(config.getint('entries', 'amount')):
            date = get_random_date(config.get('dates', 'start_date'),
                                config.get('dates', 'end_date'),
                                random())

            data = " ".join(map(lambda _: choice(words), range(10)))
            log_entries.append(f"{date}: {data}\n")

        for log_entry in sorted(log_entries):
            sample_log_file.write(log_entry)


if __name__ == "__main__":
    generate_sample_log_file()
