#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 14:18
# @Author : 余少琪


import jsonpath
from utils import sql_switch
from utils.logUtils.logControl import ERROR, WARNING
from Enums.assertType_enum import AssertType


class Assert:

    def __init__(self, assert_data: dict):
        self.assert_data = assert_data

    @staticmethod
    def _check_params(response_data: dict, sql_data: dict):
        """

        :param response_data: 响应数据
        :param sql_data: 数据库数据
        :return:
        """
        # 用例如果不执行，接口返回的相应数据和数据库断言都是 False，这里则判断跳过断言判断
        if response_data is False and sql_data is False:
            return False
        else:
            # 判断断言的数据类型
            if isinstance(response_data, dict) and isinstance(sql_data, dict):
                pass
            else:
                raise ValueError("response_data、sql_data、assert_data的数据类型必须要是字典类型")

    @staticmethod
    def _assert_type(key: any, types: str, value: any):
        """

        :param key:
        :param types:
        :param value:
        :return:
        """
        try:
            if types == AssertType.EQUAL.value:
                assert key == value
            elif types == AssertType.NOTEQUAL.value:
                assert key != value
            elif types.upper() == AssertType.IN.value:
                assert key in value
            elif types.upper() == AssertType.NO_TIN.value:
                assert key not in value

            else:
                raise ValueError(f"断言失败，目前不支持{types}断言类型，如需新增断言类型，请联系管理员")
            # 正常断言的数据，需要则开启
            # INFO.logger.info("断言成功, 预期值:{}, 断言类型{}, 实际值{}".format(value, types, key))

        except AssertionError:
            ERROR.logger.error("断言失败, 预期值:{}, 断言类型{}, 实际值{}".format(value, types, key))
            raise

    def sql_switch_handle(self, sql_data, assert_value, key, values, resp_data) -> None:
        """

        :param sql_data: 测试用例中的sql
        :param assert_value: 断言内容
        :param key:
        :param values:
        :param resp_data: 预期结果
        :return:
        """
        # 判断数据库为开关为关闭状态
        if sql_switch() is False:
            WARNING.logger.warning(f"检测到数据库状态为关闭状态，程序已为您跳过此断言，断言值:{values}")
        # 数据库开关为开启
        if sql_switch():
            # 判断当用例走的数据数据库断言，但是用例中未填写SQL
            if sql_data == {'sql': None}:
                raise ValueError("请在用例中添加您要查询的SQL语句。")
            # 走正常SQL断言逻辑
            else:
                res_sql_data = jsonpath.jsonpath(sql_data, assert_value)[0]
                # 判断mysql查询出来的数据类型如果是bytes类型，转换成str类型
                if isinstance(res_sql_data, bytes):
                    res_sql_data = res_sql_data.decode('utf=8')
                self._assert_type(types=self.assert_data[key]['type'], key=resp_data[0], value=res_sql_data)

    def assert_type_handle(self, assert_type, sql_data, assert_value, key, values, resp_data) -> None:
        # 判断断言类型
        if assert_type == 'SQL':
            self.sql_switch_handle(sql_data, assert_value, key, values, resp_data)
        # 判断assertType为空的情况下，则走响应断言
        elif assert_type is None:
            self._assert_type(types=self.assert_data[key]['type'], key=resp_data[0], value=assert_value)
        else:
            raise ValueError("断言失败，目前只支持数据库断言和响应断言")

    def assert_equality(self, response_data: dict, sql_data: dict):
        # 判断数据类型
        if self._check_params(response_data, sql_data) is not False:
            for key, values in self.assert_data.items():
                assert_value = self.assert_data[key]['value']  # 获取 yaml 文件中的期望value值
                assert_jsonpath = self.assert_data[key]['jsonpath']  # 获取到 yaml断言中的jsonpath的数据
                assert_type = self.assert_data[key]['AssertType']
                # 从yaml获取jsonpath，拿到对象的接口响应数据
                resp_data = jsonpath.jsonpath(response_data, assert_jsonpath)

                # jsonpath 如果数据获取失败，会返回False，判断获取成功才会执行如下代码
                if resp_data is not False:
                    # 判断断言类型
                    self.assert_type_handle(assert_type, sql_data, assert_value, key, values, resp_data)
                else:
                    ERROR.logger.error("JsonPath值获取失败{}".format(assert_jsonpath))
                    raise ValueError(f"JsonPath值获取失败{assert_jsonpath}")
        else:
            pass


if __name__ == '__main__':
    pass
