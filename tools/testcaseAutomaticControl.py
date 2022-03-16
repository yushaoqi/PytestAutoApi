#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/29 15:38
# @Author : 余少琪

import os
from random import random

from config.setting import ConfigHandler
from tools.yamlControl import GetYamlData
from tools import writePageFiles, writeTestCaseFile


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
            for filePath in files:
                path = os.path.join(root, filePath)
                if '.yaml' in path:
                    filename.append(path)
        return filename

    @classmethod
    def caseDatePath(cls) -> str:
        """返回 yaml 用例文件路径"""
        return ConfigHandler.data_path

    @classmethod
    def casePath(cls):
        """ 存放用例代码路径"""
        return ConfigHandler.case_path

    def fileName(self, file):
        """
        通过 yaml文件的命名，将名称转换成 py文件的名称
        :param file: yaml 文件路径
        :return:  示例： DateDemo.py
        """
        i = len(self.caseDatePath())
        yamlPath = file[i:]
        # 路径转换
        FileName = yamlPath.replace('.yaml', '.py')

        return FileName

    def libPagePath(self, filePath):
        """
        根据 yaml中的用例数据，生成对应分成中 lib 层代码路径
        :param filePath: yaml用例路径
        :return: D:\\Project\\lib\\DateDemo.py
        """
        return ConfigHandler.lib_path + self.fileName(filePath)

    def getPackagePath(self, filePath):
        """
        根据不同的层级，获取 test_case 中需要依赖的包
        :return: from lib.test_demo import DateDemo
        """
        LIB_PATH = self.fileName(filePath)
        i = LIB_PATH.split("\\")
        # 判断多层目录下的导报结构
        if len(i) > 1:
            PackagePath = "from lib"
            for files in i:
                # 去掉路径中的 .py
                if '.py' in files:
                    files = files[:-3]
                PackagePath += "." + files
            # 正常完整版本的多层结构导包路径
            PackagePath += ' import' + ' ' + i[-1][:-3]
            return PackagePath
        # 判断一层目录下的导报结构
        elif len(i) == 1:
            return f"from lib.{i[0][:-3]} import {i[0][:-3]}"

    def testCasePath(self, filePath):
        """
        根据 yaml 中的用例，生成对应 testCase 层代码的路径
        :param filePath: yaml用例路径
        :return: D:\\Project\\test_case\\test_case_demo.py
        """
        PATH = self.fileName(filePath).split('\\')
        # 判断生成的 testcase 文件名称，需要以test_ 开头
        CASE_NAME = PATH[-1] = PATH[-1].replace(PATH[-1], "test_" + PATH[-1])
        NEW_NAME = "\\".join(PATH)
        return ConfigHandler.case_path + NEW_NAME, CASE_NAME

    @classmethod
    def testCaseDetail(cls, filePath):
        """
        获取用例描述
        :param filePath: yaml 用例路径
        :return:
        """
        return GetYamlData(filePath).get_yaml_data()[0]['detail']

    def testClassTitle(self, filePath):
        """
        自动生成类名称
        :param filePath:
        :return:
        """
        return os.path.split(self.libPagePath(filePath))[1][:-3]

    def funcTitle(self, filePath):
        """
        函数名称
        :param filePath: yaml 用例路径
        :return:
        """
        _CLASS_NAME = self.testClassTitle(filePath)
        return _CLASS_NAME[0].lower() + _CLASS_NAME[1:]

    @classmethod
    def allureEpic(cls, filePath):
        """
        用于 allure 报告装饰器中的内容 @allure.epic("项目名称")
        :param filePath:
        :return:
        """
        return GetYamlData(filePath).get_yaml_data()[0]['allureEpic']

    @classmethod
    def allureFeature(cls, filePath):
        """
        用于 allure 报告装饰器中的内容 @allure.feature("模块名称")
        :param filePath:
        :return:
        """
        return GetYamlData(filePath).get_yaml_data()[0]['allureFeature']

    def mkDir(self, filePath):
        """ 判断生成自动化代码的路径是否存在，如果不存在，则自动创建 """
        _LibDirPath = os.path.split(self.libPagePath(filePath))[0]

        _CaseDirPath = os.path.split(self.testCasePath(filePath)[0])[0]
        _PathList = [_LibDirPath, _CaseDirPath]
        for i in _PathList:
            if not os.path.exists(i):
                os.makedirs(i)

    def yamlPath(self, filePath):
        """
        生成动态 yaml 路径, 主要处理业务分层场景
        :param filePath: 如业务有多个层级, 则获取到每一层/test_demo/DateDemo.py
        :return:
        """
        i = len(self.caseDatePath())
        return filePath[i:]

    def testCaseAutomatic(self):
        """ 自动生成 测试代码"""
        filePath = self._getAllFiles()

        for file in filePath:
            # # # 判断文件如果已存在，则不会重复写入
            self.mkDir(file)
            print(self.getPackagePath(file))

            writePageFiles(self.testClassTitle(file), self.funcTitle(file), self.testCaseDetail(file),
                           self.libPagePath(file), self.yamlPath(file))

            writeTestCaseFile(self.allureEpic(file), self.allureFeature(file), self.testClassTitle(file),
                              self.funcTitle(file), self.testCaseDetail(file), self.testCasePath(file)[0],
                              self.yamlPath(file), self.testCasePath(file)[1], self.getPackagePath(file))


if __name__ == '__main__':
    TestCaseAutomaticGeneration().testCaseAutomatic()

