#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 23:12
# @Author : 余少琪
import traceback

import pytest
import os
from tools.sendmailControl import SendEmail
from tools.logControl import INFO
from tools.yamlControl import GetYamlData
from config.setting import ConfigHandler


def run():
    # 从配置文件中获取项目名称
    ProjectName = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]
    try:
        INFO.logger.info(
            """
                             _    _         _      _____         _
              __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
             / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
            | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
             \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
                  |_|
                  开始执行{}项目...
                """.format(ProjectName)
        )
        pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning', '--alluredir', './report/tmp'])
        # os.system(f"allure serve ./report/tmp -p 9999")

    except Exception:
        # 如有异常，相关异常发送邮件
        e = traceback.format_exc()
        send_email = SendEmail()
        send_email.error_mail(e)
        raise


if __name__ == '__main__':
    run()


