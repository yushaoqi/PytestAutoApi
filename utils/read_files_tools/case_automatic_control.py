#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 13:22
# @Author : 余少琪
"""
import os
from typing import Text, Dict
from common.setting import ensure_path_sep
from utils.read_files_tools.testcase_template import write_testcase_file
from utils.read_files_tools.yaml_control import GetYamlData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.other_tools.exceptions import ValueNotFoundError


class TestCaseAutomaticGeneration:
    """自动生成自动化测试中的test_case代码"""

    @staticmethod
    def case_date_path() -> Text:
        """返回 yaml 用例文件路径"""
        return ensure_path_sep("\\data")

    @staticmethod
    def case_path() -> Text:
        """ 存放用例代码路径"""
        return ensure_path_sep("\\test_case")

    def file_name(self, file: Text) -> Text:
        """
        通过 yaml文件的命名，将名称转换成 py文件的名称
        :param file: yaml 文件路径
        :return:  示例： DateDemo.py
        """
        i = len(self.case_date_path())
        yaml_path = file[i:]
        file_name = None
        # 路径转换
        if '.yaml' in yaml_path:
            file_name = yaml_path.replace('.yaml', '.py')
        elif '.yml' in yaml_path:
            file_name = yaml_path.replace('.yml', '.py')
        return file_name

    def get_case_path(self, file_path: Text) -> tuple:
        """
        根据 yaml 中的用例，生成对应 testCase 层代码的路径
        :param file_path: yaml用例路径
        :return: D:\\Project\\test_case\\test_case_demo.py, test_case_demo.py
        """

        # 这里通过“\\” 符号进行分割，提取出来文件名称
        path = self.file_name(file_path).split(os.sep)
        # 判断生成的 testcase 文件名称，需要以test_ 开头
        case_name = path[-1] = path[-1].replace(path[-1], "test_" + path[-1])
        new_name = os.sep.join(path)
        return ensure_path_sep("\\test_case" + new_name), case_name

    def get_test_class_title(self, file_path: Text) -> Text:
        """
        自动生成类名称
        :param file_path:
        :return: sup_apply_list --> SupApplyList
        """
        # 提取文件名称
        _file_name = os.path.split(self.file_name(file_path))[1][:-3]
        _name = _file_name.split("_")
        _name_len = len(_name)
        # 将文件名称格式，转换成类名称: sup_apply_list --> SupApplyList
        for i in range(_name_len):
            _name[i] = _name[i].capitalize()
        _class_name = "".join(_name)

        return _class_name

    @staticmethod
    def error_message(param_name, file_path):
        """
        用例中填写不正确的相关提示
        :return:
        """
        msg = f"用例中未找到 {param_name} 参数值，请检查新增的用例中是否填写对应的参数内容" \
              "如已填写，可能是 yaml 参数缩进不正确\n" \
              f"用例路径: {file_path}"
        return msg

    def func_title(self, file_path: Text) -> Text:
        """
        函数名称
        :param file_path: yaml 用例路径
        :return:
        """

        _file_name = os.path.split(self.file_name(file_path))[1][:-3]
        return _file_name

    @staticmethod
    def allure_epic(case_data: Dict, file_path) -> Text:
        """
        用于 allure 报告装饰器中的内容 @allure.epic("项目名称")
        :param file_path: 用例路径
        :param case_data: 用例数据
        :return:
        """
        try:
            return case_data['case_common']['allureEpic']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureEpic",
                file_path=file_path
            )) from exc

    @staticmethod
    def allure_feature(case_data: Dict, file_path) -> Text:
        """
        用于 allure 报告装饰器中的内容 @allure.feature("模块名称")
        :param file_path:
        :param case_data:
        :return:
        """
        try:
            return case_data['case_common']['allureFeature']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureFeature",
                file_path=file_path
            )) from exc

    @staticmethod
    def allure_story(case_data: Dict, file_path) -> Text:
        """
        用于 allure 报告装饰器中的内容  @allure.story("测试功能")
        :param file_path:
        :param case_data:
        :return:
        """
        try:
            return case_data['case_common']['allureStory']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureStory",
                file_path=file_path
            )) from exc

    def mk_dir(self, file_path: Text) -> None:
        """ 判断生成自动化代码的文件夹路径是否存在，如果不存在，则自动创建 """
        # _LibDirPath = os.path.split(self.libPagePath(filePath))[0]

        _case_dir_path = os.path.split(self.get_case_path(file_path)[0])[0]
        if not os.path.exists(_case_dir_path):
            os.makedirs(_case_dir_path)

    @staticmethod
    def case_ids(test_case):
        """
        获取用例 ID
        :param test_case: 测试用例内容
        :return:
        """
        ids = []
        for k, v in test_case.items():
            if k != "case_common":
                ids.append(k)
        return ids

    def yaml_path(self, file_path: Text) -> Text:
        """
        生成动态 yaml 路径, 主要处理业务分层场景
        :param file_path: 如业务有多个层级, 则获取到每一层/test_demo/DateDemo.py
        :return: Login/common.yaml
        """
        i = len(self.case_date_path())
        # 兼容 linux 和 window 操作路径
        yaml_path = file_path[i:].replace("\\", "/")
        return yaml_path

    def get_case_automatic(self) -> None:
        """ 自动生成 测试代码"""
        file_path = get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True)

        for file in file_path:
            # 判断代理拦截的yaml文件，不生成test_case代码
            if 'proxy_data.yaml' not in file:
                # 判断用例需要用的文件夹路径是否存在，不存在则创建
                self.mk_dir(file)
                yaml_case_process = GetYamlData(file).get_yaml_data()
                self.case_ids(yaml_case_process)
                write_testcase_file(
                    allure_epic=self.allure_epic(case_data=yaml_case_process, file_path=file),
                    allure_feature=self.allure_feature(yaml_case_process, file_path=file),
                    class_title=self.get_test_class_title(file),
                    func_title=self.func_title(file),
                    case_path=self.get_case_path(file)[0],
                    case_ids=self.case_ids(yaml_case_process),
                    file_name=self.get_case_path(file)[1],
                    allure_story=self.allure_story(case_data=yaml_case_process, file_path=file)
                    )


if __name__ == '__main__':
    TestCaseAutomaticGeneration().get_case_automatic()
