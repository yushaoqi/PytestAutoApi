#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/14 22:06
# @Author : 余少琪

import allure
import json
import datetime
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
                str(var),
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


def getNotificationType():
    # 获取报告通知类型，是发送钉钉还是企业邮箱
    Date = GetYamlData(ConfigHandler.config_path).get_yaml_data()['NotificationType']
    return Date


def writePageFiles(classTitle, funcTitle, caseDetail, casePath, yamlPath):
    """
        自动写成 py 文件
        :param yamlPath:
        :param casePath: 生成的py文件地址
        :param classTitle: 类名称, 读取用例中的 caseTitle 作为类名称
        :param funcTitle: 函数名称 caseTitle，首字母小写
        :param caseDetail: 函数描述，读取用例中的描述内容，做为函数描述
        :return:
        """
    Author = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TestName']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {Author}


from tools.requestControl import RequestControl
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler


class {classTitle}(object):
    @staticmethod
    def {funcTitle}(inData):
        """
        {caseDetail}
        :param inData:
        :return:
        """

        resp = RequestControl().HttpRequest(inData['method'], inData)
        return resp


if __name__ == '__main__':
    path = GetCaseData(ConfigHandler.data_path + r'{yamlPath}').get_yaml_case_data()[0]
    data = {classTitle}().{funcTitle}(path)
    print(data)
        '''
    with open(casePath, 'w', encoding="utf-8") as f:
        f.write(page)


def writeTestCaseFile(allureEpic, allureFeature, classTitle, funcTitle, caseDetail, casePath, yamlPath, fileName, PackagePath):
    """

        :param allureEpic: 项目名称
        :param allureFeature: 模块名称
        :param classTitle: 类名称
        :param funcTitle: 函数名称
        :param caseDetail:  用例描述
       :param casePath: case 路径
        :param yamlPath: yaml 文件路径
        :return:
        """
    Author = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TestName']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {Author}


import allure
import pytest
from config.setting import ConfigHandler
from tools.yamlControl import GetCaseData
{PackagePath}
from tools.assertControl import Assert

TestData = GetCaseData(ConfigHandler.merchant_data_path + r'{yamlPath}').get_yaml_case_data()


@allure.epic("{allureEpic}")
@allure.feature("{allureFeature}")
class Test{classTitle}:

    @allure.story("这是一个测试的demo接口")
    @pytest.mark.parametrize('inData', TestData)
    def test_{funcTitle}(self, inData):
        """
        {caseDetail}
        :param :
        :return:
        """

        res = {classTitle}().{funcTitle}(inData)
        Assert(inData['resp']).assertEquality(responseData=res[0], sqlData=res[1])


if __name__ == '__main__':
    pytest.main(['{fileName}', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning', "--reruns=2", "--reruns-delay=2"])
'''
    with open(casePath, 'w', encoding="utf-8") as f:
        f.write(page)
