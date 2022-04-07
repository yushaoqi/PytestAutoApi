#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:47
# @Author : 余少琪

import time
from datetime import datetime


def countMilliseconds():
    """
    计算时间
    :return:
    """
    access_start = datetime.now()
    access_end = datetime.now()
    access_delta = (access_end - access_start).seconds * 1000
    return access_delta


def Timestamp_conversion(timeStr: str) -> int:
    """
    时间戳转换，将日期格式转换成时间戳
    :param timeStr: 时间
    :return:
    """

    try:
        datetimeFormat = datetime.strptime(str(timeStr), "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(datetimeFormat.timetuple()) * 1000.0 + datetimeFormat.microsecond / 1000.0)
        return timestamp
    except ValueError:
        raise '日期格式错误, 需要传入得格式为 "%Y-%m-%d %H:%M:%S" '


def Time_conversion(timeNum: int):
    """
    时间戳转换成日期
    :param timeNum:
    :return:
    """
    if isinstance(timeNum, int):
        timeStamp = float(timeNum / 1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    else:
        raise "请传入正确的时间戳"


def NowTime():
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

