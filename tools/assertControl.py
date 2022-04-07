#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 21:03
# @Author : 余少琪
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler
import jsonpath
from tools.logControl import ERROR, WARNING
from tools import SqlSwitch


class Transmission:
    EQUAL: str = "=="
    NOTEQUAL: str = "!="
    IN: str = "IN"
    NOTIN: str = "NOTIN"


class Assert:

    def __init__(self, assert_date: dict):
        self.GetCaseData = GetCaseData(ConfigHandler.merchant_data_path + r'\ShopInfo\GetSupplierInfo.yaml')
        self.assertData = assert_date

    @staticmethod
    def _check_params(response_data: dict, sql_data: dict):
        """

        :param response_data: 响应数据
        :param sql_data: 数据库数据
        :return:
        """
        # 判断断言的数据类型
        if isinstance(response_data, dict) and isinstance(sql_data, dict):
            pass
        else:
            raise ValueError("responseData、sqlData、assertData的数据类型必须要是字典类型")

    @staticmethod
    def _assert_type(key: any, assert_type: str, value: any):
        """

        :param key:
        :param assert_type:
        :param value:
        :return:
        """
        try:
            if assert_type == Transmission.EQUAL:
                assert key == value
            elif assert_type == Transmission.NOTEQUAL:
                assert key != value
            elif assert_type.upper() == Transmission.IN:
                assert key in value
            elif assert_type.upper() == Transmission.NOTIN:
                assert key not in value

            else:
                raise ValueError(f"断言失败，目前不支持{assert_type}断言类型，如需新增断言类型，请联系管理员")
            # 断言成功的日志，需要的话可以自动开启
            # INFO.logger.info("断言成功, 预期值:{}, 断言类型{}, 实际值{}".format(value, Type, key))

        except AssertionError:
            ERROR.logger.error("断言失败, 预期值:{}, 断言类型{}, 实际值{}".format(value, assert_type, key))
            raise

    def sql_switch_handle(self, sql_date, assert_value, key, values, resp_data) -> None:
        """

        :param sql_date: 测试用例中的sql
        :param assert_value: 断言内容
        :param key:
        :param values:
        :param resp_data: 预期结果
        :return:
        """
        # 判断数据库为开关为关闭状态
        if SqlSwitch() is False:
            WARNING.logger.warning(f"检测到数据库状态为关闭状态，程序已为您跳过此断言，断言值:{values}")
        # 数据库开关为开启
        if SqlSwitch():
            # 判断当用例走的数据数据库断言，但是用例中未填写SQL
            if sql_date == {'sql': None}:
                raise ValueError("请在用例中添加您要查询的SQL语句。")
            # 走正常SQL断言逻辑
            else:
                res_sql_data = jsonpath.jsonpath(sql_date, assert_value)[0]
                # 判断mysql查询出来的数据类型如果是bytes类型，转换成str类型
                if isinstance(res_sql_data, bytes):
                    res_sql_data = res_sql_data.decode('utf=8')
                self._assert_type(assert_type=self.assertData[key]['type'], key=resp_data[0], value=res_sql_data)

    def assert_type_handle(self, assert_type, sql_data, assert_value, key, values, resp_data) -> None:
        # 判断断言类型
        if assert_type == 'SQL':
            self.sql_switch_handle(sql_data, assert_value, key, values, resp_data)
        # 判断assertType为空的情况下，则走响应断言
        elif assert_type is None:
            self._assert_type(assert_type=self.assertData[key]['type'], key=resp_data[0], value=resp_data)
        else:
            raise ValueError("断言失败，目前只支持数据库断言和响应断言")

    def assert_equality(self, response_data: dict, sql_data: dict) -> None:
        # 判断数据类型
        self._check_params(response_data, sql_data)
        for key, values in self.assertData.items():
            assert_value = self.assertData[key]['value']  # 获取 yaml 文件中的期望value值
            assert_json_path = self.assertData[key]['jsonpath']  # 获取到 yaml断言中的jsonpath的数据
            assert_type = self.assertData[key]['AssertType']
            # 从yaml获取jsonpath，拿到对象的接口响应数据
            resp_data = jsonpath.jsonpath(response_data, assert_json_path)

            # jsonpath 如果数据获取失败，会返回False，判断获取成功才会执行如下代码
            if resp_data is not False:
                # 判断断言类型
                self.assert_type_handle(assert_type, sql_data, assert_value, key, values, resp_data)
            else:
                ERROR.logger.error("JsonPath值获取失败{}".format(assert_json_path))
                raise
