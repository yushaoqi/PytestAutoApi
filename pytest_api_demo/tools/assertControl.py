#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 21:03
# @Author : 余少琪
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler
import jsonpath
from tools.logControl import INFO, ERROR, WARNING
from tools import slash


class Transmission:
    EQUAL: str = "=="
    NOTEQUAL: str = "!="
    IN: str = "IN"
    NOTIN: str = "NOTIN"


class Assert:

    def __init__(self, assertData: dict):
        self.GetCaseData = GetCaseData(ConfigHandler.merchant_data_path + r'/ShopInfo/GetSupplierInfo.yaml')
        self.assertData = assertData

    @staticmethod
    def _checkParams(responseData: dict, sqlData: dict):
        """

        :param responseData: 响应数据
        :param sqlData: 数据库数据
        :return:
        """
        # 判断断言的数据类型
        if isinstance(responseData, dict) and isinstance(sqlData, dict):
            pass
        else:
            raise "responseData、sqlData、assertData的数据类型必须要是字典类型"

    @staticmethod
    def _switch():
        # 获取数据库开关
        switch = GetCaseData(ConfigHandler.config_path).get_yaml_data()['MySqlDB']["switch"]
        return switch

    @staticmethod
    def _assertType(key: any, Type: str, value: any):
        """

        :param key:
        :param Type:
        :param value:
        :return:
        """
        try:
            if Type == Transmission.EQUAL:
                assert key == value
            elif Type == Transmission.NOTEQUAL:
                assert key != value
            elif Type.upper() == Transmission.IN:
                assert key in value
            elif Type.upper() == Transmission.NOTIN:
                assert key not in value

            else:
                raise f"断言失败，目前不支持{Type}断言类型，如需新增断言类型，请联系管理员"

            INFO.logger.info("断言成功, 预期值:{}, 断言类型{}, 实际值{}".format(key, Type, value))

        except AssertionError:
            ERROR.logger.error("断言失败, 预期值:{}, 断言类型{}, 实际值{}".format(key, Type, value))
            raise

    def assertEquality(self, responseData: dict, sqlData: dict):
        # 判断数据类型
        self._checkParams(responseData, sqlData)
        global getSqlData
        for key, values in self.assertData.items():
            assertValue = self.assertData[key]['value']  # 获取 yaml 文件中的期望value值
            assertJsonPath = self.assertData[key]['jsonpath']  # 获取到 yaml断言中的jsonpath的数据
            assertType = self.assertData[key]['AssertType']
            # 从yaml获取jsonpath，拿到对象的接口响应数据
            respData = jsonpath.jsonpath(responseData, assertJsonPath)

            # jsonpath 如果数据获取失败，会返回False，判断获取成功才会执行如下代码
            if respData is not False:
                if assertType == 'SQL':
                    # 判断数据库为开关为关闭状态
                    if self._switch() is False:
                        WARNING.logger.warning(f"检测到数据库状态为关闭状态，程序已为您跳过此断言，断言值:{values}")
                    # 数据库开关为开启
                    if self._switch():
                        # 判断当用例走的数据数据库断言，但是用例中未填写SQL
                        if sqlData == {'sql': None}:
                            raise "请在用例中添加您要查询的SQL语句。"
                        # 走正常SQL断言逻辑
                        else:
                            ResSqlData = jsonpath.jsonpath(sqlData, assertValue)[0]
                            # 判断mysql查询出来的数据类型如果是bytes类型，转换成str类型
                            if isinstance(ResSqlData, bytes):
                                ResSqlData = ResSqlData.decode('utf=8')
                            self._assertType(Type=self.assertData[key]['type'], key=respData[0], value=ResSqlData)
                # 判断assertType为空的情况下，则走响应断言
                elif assertType is None:
                    self._assertType(Type=self.assertData[key]['type'], key=respData[0], value=assertValue)
                else:
                    raise "断言失败，目前只支持数据库断言和响应断言"
            else:
                ERROR.logger.error("JsonPath值获取失败{}".format(assertJsonPath))
                raise


if __name__ == '__main__':
    pass

