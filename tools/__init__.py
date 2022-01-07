#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/14 22:06
# @Author : 余少琪

import allure
import json
from config.setting import get_current_system, ConfigHandler
from tools.yamlControl import GetYamlData


def allure_step(step: str, var: str) -> None:
    """
    :param step: 步骤及附件名称
    :param var: 附件内容
    """
    with allure.step(step):
        allure.attach(
            json.dumps(
                var,
                ensure_ascii=False,
                indent=4),
            step,
            allure.attachment_type.JSON)


def allure_step_no(step: str):
    """
    无附件的操作步骤
    :param step: 步骤名称
    :return:
    """
    with allure.step(step):
        pass


def slash():
    # 判断系统路径
    SLASH = '\\'

    # 判断当前操作系统
    if get_current_system() == 'Linux' or get_current_system() == "Darwin":
        SLASH = '/'

    return SLASH


def SqlSwitch() -> bool:
    """获取数据库开关"""
    switch = GetYamlData(ConfigHandler.config_path) \
        .get_yaml_data()['MySqlDB']["switch"]
    return switch
