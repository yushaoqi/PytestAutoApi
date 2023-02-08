#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 14:43
# @Author : 余少琪
"""
统计请求运行时长装饰器，如请求响应时间超时
程序中会输入红色日志，提示时间 http 请求超时，默认时长为 3000ms
"""
from utils.logging_tool.log_control import ERROR


def execution_duration(number: int):
    """
    封装统计函数执行时间装饰器
    :param number: 函数预计运行时长
    :return:
    """

    def decorator(func):
        def swapper(*args, **kwargs):
            res = func(*args, **kwargs)
            run_time = res.res_time
            # 计算时间戳毫米级别，如果时间大于number，则打印 函数名称 和运行时间
            if run_time > number:
                ERROR.logger.error(
                    "\n==============================================\n"
                    "测试用例执行时间较长，请关注.\n"
                    "函数运行时间: %s ms\n"
                    "测试用例相关数据: %s\n"
                    "================================================="
                    , run_time, res)
            return res
        return swapper
    return decorator
