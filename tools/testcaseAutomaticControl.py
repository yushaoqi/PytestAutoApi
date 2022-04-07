#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/29 15:38
# @Author : 余少琪

import os
from config.setting import ConfigHandler
from tools.yamlControl import GetYamlData
from tools import writePageFiles, writeTestCaseFile


class TestCaseAutomaticGeneration:
    """自动生成自动化测试中的page代码"""

    # TODO 自动生成测试代码
    def __init__(self):
        pass

    @classmethod
    def _get_all_files(cls):
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
    def case_date_path(cls) -> str:
        """返回 yaml 用例文件路径"""
        return ConfigHandler.data_path

    @classmethod
    def case_path(cls):
        """ 存放用例代码路径"""
        return ConfigHandler.case_path

    def file_name(self, file):
        """
        通过 yaml文件的命名，将名称转换成 py文件的名称
        :param file: yaml 文件路径
        :return:  示例： DateDemo.py
        """
        i = len(self.case_date_path())
        yaml_path = file[i:]
        # 路径转换
        file_name = yaml_path.replace('.yaml', '.py')

        return file_name

    def lib_page_path(self, file_path):
        """
        根据 yaml中的用例数据，生成对应分成中 lib 层代码路径
        :param file_path: yaml用例路径
        :return: D:\\Project\\lib\\DateDemo.py
        """
        return ConfigHandler.lib_path + self.file_name(file_path)

    def get_package_path(self, file_path):
        """
        根据不同的层级，获取 test_case 中需要依赖的包
        :return: from lib.test_demo import DateDemo
        """
        lib_path = self.file_name(file_path)
        i = lib_path.split("\\")
        # 判断多层目录下的导报结构
        if len(i) > 1:
            package_path = "from lib"
            for files in i:
                # 去掉路径中的 .py
                if '.py' in files:
                    files = files[:-3]
                package_path += "." + files
            # 正常完整版本的多层结构导包路径
            package_path += ' import' + ' ' + i[-1][:-3]
            return package_path
        # 判断一层目录下的导报结构
        elif len(i) == 1:
            return f"from lib.{i[0][:-3]} import {i[0][:-3]}"

    def test_case_path(self, file_path):
        """
        根据 yaml 中的用例，生成对应 testCase 层代码的路径
        :param file_path: yaml用例路径
        :return: D:\\Project\\test_case\\test_case_demo.py
        """
        path = self.file_name(file_path).split('\\')
        # 判断生成的 testcase 文件名称，需要以test_ 开头
        case_name = path[-1] = path[-1].replace(path[-1], "test_" + path[-1])
        new_name = "\\".join(path)
        return ConfigHandler.case_path + new_name, case_name

    @classmethod
    def test_case_detail(cls, file_path):
        """
        获取用例描述
        :param file_path: yaml 用例路径
        :return:
        """
        return GetYamlData(file_path).get_yaml_data()[0]['detail']

    def test_class_title(self, file_path):
        """
        自动生成类名称
        :param file_path:
        :return:
        """
        return os.path.split(self.lib_page_path(file_path))[1][:-3]

    def func_title(self, file_path):
        """
        函数名称
        :param file_path: yaml 用例路径
        :return:
        """
        _CLASS_NAME = self.test_class_title(file_path)
        return _CLASS_NAME[0].lower() + _CLASS_NAME[1:]

    @classmethod
    def allure_epic(cls, file_path):
        """
        用于 allure 报告装饰器中的内容 @allure.epic("项目名称")
        :param file_path:
        :return:
        """
        return GetYamlData(file_path).get_yaml_data()[0]['allureEpic']

    @classmethod
    def allure_feature(cls, file_path):
        """
        用于 allure 报告装饰器中的内容 @allure.feature("模块名称")
        :param file_path:
        :return:
        """
        return GetYamlData(file_path).get_yaml_data()[0]['allureFeature']

    def mk_dir(self, file_path):
        """ 判断生成自动化代码的路径是否存在，如果不存在，则自动创建 """
        _LibDirPath = os.path.split(self.lib_page_path(file_path))[0]

        _CaseDirPath = os.path.split(self.test_case_path(file_path)[0])[0]
        _PathList = [_LibDirPath, _CaseDirPath]
        for i in _PathList:
            if not os.path.exists(i):
                os.makedirs(i)

    def yaml_path(self, file_path):
        """
        生成动态 yaml 路径, 主要处理业务分层场景
        :param file_path: 如业务有多个层级, 则获取到每一层/test_demo/DateDemo.py
        :return:
        """
        i = len(self.case_date_path())
        return file_path[i:]

    def test_case_automatic(self):
        """ 自动生成 测试代码"""
        file_path = self._get_all_files()

        for file in file_path:
            # # # 判断文件如果已存在，则不会重复写入
            self.mk_dir(file)
            print(self.get_package_path(file))

            writePageFiles(self.test_class_title(file), self.func_title(file), self.test_case_detail(file),
                           self.lib_page_path(file), self.yaml_path(file))

            writeTestCaseFile(self.allure_epic(file), self.allure_feature(file), self.test_class_title(file),
                              self.func_title(file), self.test_case_detail(file), self.test_case_path(file)[0],
                              self.yaml_path(file), self.test_case_path(file)[1], self.get_package_path(file))


if __name__ == '__main__':
    TestCaseAutomaticGeneration().test_case_automatic()
