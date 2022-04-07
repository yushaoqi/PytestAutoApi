#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 17:42
# @Author : 余少琪

from enum import Enum


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    # json 类型
    JSON = "JSON"
    # PARAMS 类型
    PARAMS = "PARAMS"
    # data 类型
    DATE = "DATE"
    # 文件类型
    FILE = 'FILE'
