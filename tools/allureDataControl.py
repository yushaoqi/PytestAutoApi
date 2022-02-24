#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/2/23 18:15
# @Author : 余少琪
import json

from setting import ConfigHandler
import os


class AllureFileClean:
    """allure 报告数据清洗，提取业务需要得数据"""

    @classmethod
    def _getAllFiles(cls) -> list:
        """ 获取所有 test-case 中的 json 文件 """
        filename = []
        # 获取所有文件下的子文件名称
        for root, dirs, files in os.walk(ConfigHandler.report_path + '/html/data/test-cases'):
            for filePath in files:
                path = os.path.join(root, filePath)
                filename.append(path)
        return filename

    def getTestCases(self):
        """ 获取所有 allure 报告中执行用例的情况"""
        # 将所有数据都收集到files中
        files = []
        for i in self._getAllFiles():
            with open(i, 'r', encoding='utf-8') as fp:
                date = json.load(fp)
                files.append(date)
        return files

    def getFailedCase(self):
        """ 获取到所有失败的用例标题和用例代码路径"""
        errorCase = []
        for i in self.getTestCases():
            if i['status'] == 'failed' or i['status'] == 'broken':
                errorCase.append((i['name'], i['fullName']))
        return errorCase

    def getFailedCasesDetail(self):
        """ 返回所有失败的测试用例相关内容 """
        Data = self.getFailedCase()
        # 判断有失败用例，则返回内容
        if len(Data) >= 1:
            values = "失败用例:\n"
            values += "        **********************************\n"
            for i in Data:
                values += "        " + i[0] + ":" + i[1] + "\n"
            return values
        else:
            # 如果没有失败用例，则返回False
            return ""

    @classmethod
    def getCaseCount(cls):
        """ 统计用例数量 """
        fileName = ConfigHandler.report_path + '/html/history/history-trend.json'
        with open(fileName, 'r', encoding='utf-8') as fp:
            date = json.load(fp)[0]['data']
        return date


class CaseCount:
    def __init__(self):
        self.AllureData = AllureFileClean()

    def passCount(self):
        """用例成功数"""
        return self.AllureData.getCaseCount()['passed']

    def failedCount(self):
        """用例失败数"""
        return self.AllureData.getCaseCount()['failed']

    def brokenCount(self):
        """用例异常数"""
        return self.AllureData.getCaseCount()['broken']

    def skippedCount(self):
        """用例跳过数"""
        return self.AllureData.getCaseCount()['skipped']

    def totalCount(self):
        """用例总数"""
        return self.AllureData.getCaseCount()['total']

    def passRate(self):
        """用例成功率"""
        # 四舍五入，保留2位小数
        try:
            passRate = round((self.passCount() + self.skippedCount()) / self.totalCount() * 100, 2)
            return passRate
        except ZeroDivisionError:
            return 0.00


if __name__ == '__main__':
    data = AllureFileClean().getCaseCount()
    print(data)
