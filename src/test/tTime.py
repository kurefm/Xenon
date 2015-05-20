# -*- coding: utf-8 -*-

import datetime
import re

TEST = ['10分钟前', '今天 12:34', '05-18 21:49', '2014-12-16 11:19', '04-09 16:22']

TIME_TYPE_1 = re.compile(r'^([0-5][0-9])[\D]+$')
TIME_TYPE_2 = re.compile(r'^[\D]+([0-1][0-9]|2[0-3])\:([0-5][0-9])$')
TIME_TYPE_3 = re.compile(r'^(0[0-9]|1[0-2])\-([0-2][0-9]|3[0-1]).([0-1][0-9]|2[0-3])\:([0-5][0-9])$')
TIME_TYPE_4 = re.compile(r'^([0-9]{4})\-(0[0-9]|1[0-2])\-([0-2][0-9]|3[0-1]).([0-1][0-9]|2[0-3])\:([0-5][0-9])$')

TIME_TYPE = [TIME_TYPE_1, TIME_TYPE_2, TIME_TYPE_3, TIME_TYPE_4]


def resolution_time(time_str):
    # n分钟前
    match = re.match(TIME_TYPE_1, time_str)
    if match:
        dt = datetime.datetime.now()

        delta = datetime.timedelta(minutes=int(match.group(1)))

        return dt - delta

    # 今天 hour:minute
    match = re.match(TIME_TYPE_2, time_str)
    if match:
        dt = datetime.datetime.now()

        hour = int(match.group(1))
        minute = int(match.group(2))

        return dt.replace(hour=hour, minute=minute)

    # month-day hour:minute
    match = re.match(TIME_TYPE_3, time_str)
    if match:
        dt = datetime.datetime.now()

        month = int(match.group(1))
        day = int(match.group(2))
        hour = int(match.group(3))
        minute = int(match.group(4))

        return dt.replace(month=month, day=day, hour=hour, minute=minute)

    # year-month-day hour:minute
    match = re.match(TIME_TYPE_4, time_str)
    if match:
        dt = datetime.datetime.now()

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))

        return dt.replace(year=year, month=month, day=day, hour=hour, minute=minute)
    else:
        raise RuntimeError("Can't match {0}".format(time_str))


if __name__ == '__main__':
    for test in TEST:
        print resolution_time(test)
