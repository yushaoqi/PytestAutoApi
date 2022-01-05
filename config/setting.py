#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 13:07
# @Author : 余少琪

import os
import platform


def get_current_system():
    """
    获取当前操作系统
    :return:
    """

    platform_system = platform.system()
    return platform_system


class ConfigHandler:
    _SLASH = '/'

    # 判断当前操作系统
    if get_current_system() == 'Linux' or get_current_system() == "Darwin":

        _SLASH = '/'

    # 项目路径
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 测试数据路径
    date_path = os.path.join(root_path, 'data' + _SLASH + "Merchant" + _SLASH + "UserLogin")

    merchant_data_path = os.path.join(root_path, 'data' + _SLASH)

    data_path = os.path.join(root_path, 'data' + _SLASH)

    cache_path = os.path.join(root_path, 'Cache' + _SLASH)

    # 测试报告路径
    report_path = os.path.join(root_path, 'report')

    json_path = os.path.join(root_path, 'data' + _SLASH + 'data.json')

    log_path = os.path.join(root_path + _SLASH + 'logs')

    info_log_path = os.path.join(root_path, 'logs' + _SLASH + 'info.log')

    error_log_path = os.path.join(root_path, 'logs' + _SLASH + 'error.log')

    if not os.path.exists(report_path):
        os.mkdir(report_path)

    config_path = os.path.join(root_path, 'config' + _SLASH + 'conf.yaml')

    token_yaml_path = os.path.join(root_path, 'data' + _SLASH + 'token.yaml')

    excel_path = os.path.join(root_path, 'data' + _SLASH)

    # lib 存放po文件
    lib_path = os.path.join(root_path, "lib")


if __name__ == '__main__':
    print(ConfigHandler.config_path)

