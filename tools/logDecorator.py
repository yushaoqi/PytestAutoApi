#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/30 23:25
# @Author : 余少琪
import os
from functools import wraps
from tools.logControl import INFO


def logDecorator(switch: bool):
    """
    封装日志装饰器, 打印请求信息
    :param switch: 定义日志开关
    :return:
    """
    # 判断参数类型是否是 int 类型
    if isinstance(switch, bool):
        def decorator(func):
            @wraps(func)
            def swapper(*args, **kwargs):
                # 判断日志为开启状态，才打印日志
                if switch:
                    res = func(*args, **kwargs)
                    if res is not None:
                        INFO.logger.info(
                            f"\n=================================================================================\n"
                            f"测试标题: {res[2]['detail']}\n"
                            f"请求方式: {res[2]['method']}\n"
                            f"请求头:   {res[2]['headers']}\n"
                            f"请求路径: {res[2]['url']}\n"
                            f"请求内容: {res[2]['data']}\n"
                            f"接口响应内容: {res[0]}\n"
                            f"数据库断言数据: {res[1]}\n"
                            f"函数名称: {func.__name__}\n"
                            "================================================================================="

                        )
                    return res
            return swapper

        return decorator
    else:
        raise TypeError("日志开关只能为 Ture 或者 False")

