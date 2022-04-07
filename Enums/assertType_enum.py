#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 18:03
# @Author : 余少琪

from enum import Enum


class AssertType(Enum):
    EQUAL = "=="
    NOTEQUAL = "!="
    IN = "IN"
    NO_TIN = "NOTIN"
