#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/29 15:38
# @Author : 余少琪
import time

from config.setting import ConfigHandler
import datetime
from tools.yamlControl import GetYamlData
import os


class TestCaseAutomaticGeneration:
    """自动生成自动化测试中的page代码"""

    # TODO 自动生成测试代码
    def __init__(self):
        pass

    @classmethod
    def _getAllFiles(cls):
        """ 获取所有 yaml 文件 """
        filename = []
        # 获取所有文件下的子文件名称
        for root, dirs, files in os.walk(ConfigHandler.data_path):
            # 过滤所有空文件
            if files:
                for i in files:
                    # 判断只返回 yaml 的文件
                    if '.yaml' in i:
                        filename.append((root, i))
        return filename

    def testCaseAutomatic(self):
        """ 自动生成 测试代码"""
        files = self._getAllFiles()
        for file in files:
            print(file)
            caseDetail = GetYamlData(
                file[0] + "\\" + file[1]
            ).get_yaml_data()[0]['detail']

            # 类名称(直接获取 yaml 文件的命名做为生成的类名称)
            classTitle = file[1][:-5]
            # 函数名称(类名称改成小写，作为函数名称)
            funcTitle = classTitle[0].lower() + classTitle[1:]
            # 生成测试用例的路径
            casePath = ConfigHandler().lib_path + '\\' + classTitle + '.py'
            # 判断只生成不存在的py文件，已存在则不写入
            if not os.path.exists(casePath):
                # yaml文件路径
                yamlPath = file[0] + "\\" + file[1]
                # TODO 根据接口生成的文件进行分组
                self.writePageFiles(classTitle, funcTitle, caseDetail, casePath, yamlPath)

    @classmethod
    def writePageFiles(cls, classTitle, funcTitle, caseDetail, casePath, yamlPath):
        """
        自动写成 py 文件
        :param yamlPath:
        :param casePath: 生成的py文件地址
        :param classTitle: 类名称, 读取用例中的 caseTitle 作为类名称
        :param funcTitle: 函数名称 caseTitle，首字母小写
        :param caseDetail: 函数描述，读取用例中的描述内容，做为函数描述
        :return:
        """

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : 余少琪


from tools.requestControl import RequestControl
from tools.yamlControl import GetCaseData


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
    path = GetCaseData(r"{yamlPath}").get_yaml_case_data()[0]
    data = {classTitle}().{funcTitle}(path)
    print(data)
        '''

        with open(casePath, 'w', encoding="utf-8") as f:
            f.write(page)


if __name__ == '__main__':
    # 定义开始时间
    TestCaseAutomaticGeneration().testCaseAutomatic()

