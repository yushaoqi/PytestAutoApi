#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/2/23 18:15
# @Author : 余少琪
import json

from setting import ConfigHandler
import os


class AllureFileClean:
    """allure 报告数据清洗，提取业务需要得数据"""

    def __init__(self):
        pass

    @classmethod
    def _get_al_files(cls) -> list:
        """ 获取所有 test-case 中的 json 文件 """
        filename = []
        # 获取所有文件下的子文件名称
        for root, dirs, files in os.walk(ConfigHandler.report_path + '/html/data/test-cases'):
            for filePath in files:
                path = os.path.join(root, filePath)
                filename.append(path)
        return filename

    def get_test_cases(self):
        """ 获取所有 allure 报告中执行用例的情况"""
        # 将所有数据都收集到files中
        files = []
        for i in self._get_al_files():
            with open(i, 'r', encoding='utf-8') as fp:
                date = json.load(fp)
                files.append(date)
        return files

    def get_failed_case(self):
        """ 获取到所有失败的用例标题和用例代码路径"""
        error_cases = []
        for i in self.get_test_cases():
            if i['status'] == 'failed' or i['status'] == 'broken':
                error_cases.append((i['name'], i['fullName']))
        return error_cases

    def get_failed_cases_detail(self):
        """ 返回所有失败的测试用例相关内容 """
        date = self.get_failed_case()
        # 判断有失败用例，则返回内容
        if len(date) >= 1:
            values = "失败用例:\n"
            values += "        **********************************\n"
            for i in date:
                values += "        " + i[0] + ":" + i[1] + "\n"
            return values
        else:
            # 如果没有失败用例，则返回False
            return ""

    @classmethod
    def get_case_count(cls):
        """ 统计用例数量 """
        file_name = ConfigHandler.report_path + '/html/history/history-trend.json'
        with open(file_name, 'r', encoding='utf-8') as fp:
            date = json.load(fp)[0]['data']
        return date


class CaseCount:
    def __init__(self):
        self.AllureData = AllureFileClean()

    def pass_count(self):
        """用例成功数"""
        return self.AllureData.get_case_count()['passed']

    def failed_count(self):
        """用例失败数"""
        return self.AllureData.get_case_count()['failed']

    def broken_count(self):
        """用例异常数"""
        return self.AllureData.get_case_count()['broken']

    def skipped_count(self):
        """用例跳过数"""
        return self.AllureData.get_case_count()['skipped']

    def total_count(self):
        """用例总数"""
        return self.AllureData.get_case_count()['total']

    def pass_rate(self):
        """用例成功率"""
        # 四舍五入，保留2位小数
        try:
            pass_rate = round((self.pass_count() + self.skipped_count()) / self.total_count() * 100, 2)
            return pass_rate
        except ZeroDivisionError:
            return 0.00


if __name__ == '__main__':
    data = AllureFileClean().get_case_count()
    print(data)
