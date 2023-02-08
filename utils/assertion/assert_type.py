#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/4/22 14:49
# @Author : 余少琪

"""
Assert 断言类型
"""

from typing import Any,  Union, Text


def equals(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """判断是否相等"""

    assert check_value == expect_value, message


def less_than(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """判断实际结果小于预期结果"""
    assert check_value < expect_value, message


def less_than_or_equals(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):

    """判断实际结果小于等于预期结果"""
    assert check_value <= expect_value, message


def greater_than(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """判断实际结果大于预期结果"""
    assert check_value > expect_value, message


def greater_than_or_equals(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """判断实际结果大于等于预期结果"""
    assert check_value >= expect_value, message


def not_equals(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """判断实际结果不等于预期结果"""
    assert check_value != expect_value, message


def string_equals(
        check_value: Text, expect_value: Any, message: Text = ""
):
    """判断字符串是否相等"""
    assert check_value == expect_value, message


def length_equals(
        check_value: Text, expect_value: int, message: Text = ""
):
    """判断长度是否相等"""
    assert isinstance(
        expect_value, int
    ), "expect_value 需要为 int 类型"
    assert len(check_value) == expect_value, message


def length_greater_than(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """判断长度大于"""
    assert isinstance(
        expect_value, (float, int)
    ), "expect_value 需要为 float/int 类型"
    assert len(str(check_value)) > expect_value, message


def length_greater_than_or_equals(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """判断长度大于等于"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert len(check_value) >= expect_value, message


def length_less_than(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """判断长度小于"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert len(check_value) < expect_value, message


def length_less_than_or_equals(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """判断长度小于等于"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value 需要为 float/int 类型"
    assert len(check_value) <= expect_value, message


def contains(check_value: Any, expect_value: Any, message: Text = ""):
    """判断期望结果内容包含在实际结果中"""
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "expect_value 需要为  list/tuple/dict/str/bytes  类型"
    assert expect_value in check_value, message


def contained_by(check_value: Any, expect_value: Any, message: Text = ""):
    """判断实际结果包含在期望结果中"""
    assert isinstance(
        expect_value, (list, tuple, dict, str, bytes)
    ), "expect_value 需要为  list/tuple/dict/str/bytes  类型"

    assert check_value in expect_value, message


def startswith(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """检查响应内容的开头是否和预期结果内容的开头相等"""
    assert str(check_value).startswith(str(expect_value)), message


def endswith(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """检查响应内容的结尾是否和预期结果内容相等"""
    assert str(check_value).endswith(str(expect_value)), message
