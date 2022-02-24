#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/28 23:05
# @Author : 余少琪
import pytest
import os
from config.setting import ConfigHandler
from tools.yamlControl import GetYamlData


_PROJECT_NAME = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]
_TEST_NAME = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TestName']


@pytest.fixture(scope="session", autouse=True)
def clear_report():
    try:
        for one in os.listdir(ConfigHandler.report_path + f'/tmp'):
            if 'json' in one:
                os.remove(ConfigHandler.report_path + f'/tmp/{one}')
            if 'txt' in one:
                os.remove(ConfigHandler.report_path + f'/tmp/{one}')
    except Exception as e:
        print("allure数据清除失败", e)

    yield


