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
    _SLASH = '\\'

    # 判断当前操作系统
    if get_current_system() == 'Linux' or get_current_system() == "Darwin":

        _SLASH = '/'

    # 项目路径
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 用例路径
    case_path = os.path.join(root_path, 'test_case' + _SLASH)
    # 测试用例数据路径
    data_path = os.path.join(root_path, 'data' + _SLASH)

    cache_path = os.path.join(root_path, 'Cache' + _SLASH)
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)

    log_path = os.path.join(root_path, 'logs' + _SLASH + 'log.log')

    info_log_path = os.path.join(root_path, 'logs' + _SLASH + 'info.log')

    error_log_path = os.path.join(root_path, 'logs' + _SLASH + 'error.log')

    warning_log_path = os.path.join(root_path, 'logs' + _SLASH + 'warning.log')

    config_path = os.path.join(root_path, 'config' + _SLASH + 'config.yaml')

    file_path = os.path.join(root_path, 'Files' + _SLASH)

    # 测试报告路径
    report_path = os.path.join(root_path, 'report')

    # lib 存放po文件
    lib_path = os.path.join(root_path, "lib" + _SLASH)

    # temp_path = os.path.join(root_path, 'report' + _SLASH + 'tmp')
    # if not os.path.exists(temp_path):
    #     os.mkdir(temp_path)


if __name__ == '__main__':
    print(ConfigHandler.cache_path)
