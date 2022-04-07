#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-03-16 13:07:13
# @Author : 余少琪


import allure
import pytest
from config.setting import ConfigHandler
from tools.yamlControl import GetCaseData
from lib.test_demo.DateDemo import DateDemo
from tools.assertControl import Assert

TestData = GetCaseData(ConfigHandler.merchant_data_path + r'test_demo\DateDemo.yaml').get_yaml_case_data()


@allure.epic("这里是测试平台名称")
@allure.feature("这里是测试模块名称")
class TestDateDemo:

    @allure.story("这是一个测试的demo接口")
    @pytest.mark.parametrize('data', TestData)
    def test_date_demo(self, date):
        """
        测试接口
        :param :
        :return:
        """

        res = DateDemo().dateDemo(date)
        Assert(date['resp']).assert_equality(response_data=res[0], sql_data=res[1])


if __name__ == '__main__':
    pytest.main(['test_DateDemo.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning', "--reruns=2",
                 "--reruns-delay=2"])
