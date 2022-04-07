#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 17:32
# @Author : 余少琪
from enum import Enum, unique


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    # 依赖响应中数据
    RESPONSE = 'response'
    # 依赖请求中的数据
    REQUEST = 'request'
    # 依赖sql中的数据
    SQL_DATA = 'sqlData'

