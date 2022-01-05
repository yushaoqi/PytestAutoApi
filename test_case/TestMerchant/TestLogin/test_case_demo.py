#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/26 20:21
# @Author : 余少琪


import allure
import os
from config.setting import ConfigHandler
from tools.yamlControl import GetCaseData
from lib.TestDemo import Demo
import pytest
from tools.assertControl import Assert

Path = GetCaseData(ConfigHandler.merchant_data_path + 'TestDemo.yaml')
TestData = Path.get_yaml_case_data()


@allure.epic("测试平台端")
@allure.feature("测试模块")
class TestShopList:

    @allure.story("这是一个测试的demo接口")
    @pytest.mark.parametrize('inData', TestData)
    def testDemo(self, inData):
        """
        测试
        :param :
        :return:
        """

        res = Demo().Demo(inData)
        Assert(inData['resp']).assertEquality(responseData=res[0], sqlData=res[1])


if __name__ == '__main__':
    pytest.main(['test_case_demo.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
