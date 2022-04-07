#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 23:24
# @Author : 余少琪

import time
from datetime import datetime


def count_milliseconds():
    """
    计算时间
    :return:
    """
    access_start = datetime.now()
    access_end = datetime.now()
    access_delta = (access_end - access_start).seconds * 1000
    return access_delta


def timestamp_conversion(time_str: str) -> int:
    """
    时间戳转换，将日期格式转换成时间戳
    :param time_str: 时间
    :return:
    """

    try:
        datetime_format = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(datetime_format.timetuple()) * 1000.0 + datetime_format.microsecond / 1000.0)
        return timestamp
    except ValueError:
        raise ValueError('日期格式错误, 需要传入得格式为 "%Y-%m-%d %H:%M:%S" ')


def time_conversion(time_num: int):
    """
    时间戳转换成日期
    :param time_num:
    :return:
    """
    if isinstance(time_num, int):
        time_stamp = float(time_num / 1000)
        time_array = time.localtime(time_stamp)
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time

    else:
        raise ValueError("请传入正确的时间戳")


def now_time() -> str:
    """
    获取当前时间, 日期格式: 2021-12-11 12:39:25
    :return:
    """
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return localtime


def get_time_for_min(minute: int) -> int:
    """
    获取几分钟后的时间戳
    @param minute: 分钟
    @return: N分钟后的时间戳
    """
    return int(time.time() + 60 * minute) * 1000


def get_now_time() -> int:
    """
    获取当前时间戳, 整形
    @return: 当前时间戳
    """
    return int(time.time()) * 1000


if __name__ == '__main__':
    print(now_time())
    time_conversion(1547450538000)
