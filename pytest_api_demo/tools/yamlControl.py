#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/24 22:08
# @Author : 余少琪
import yaml.scanner
import os
from tools.regularControl import regular
from config.setting import ConfigHandler
from tools.logControl import ERROR


class GetYamlData:

    def __init__(self, fileDir):
        self.fileDir = fileDir

    def get_yaml_data(self):
        """
        获取 yaml 中的数据
        :param: fileDir:
        :return:
        """
        # 判断文件是否存在
        if os.path.exists(self.fileDir):
            data = open(self.fileDir, 'r', encoding='utf-8')
            res = yaml.load(data, Loader=yaml.FullLoader)
            return res
        else:
            raise FileNotFoundError("文件路径不存在")


class GetCaseData(GetYamlData):

    def get_different_formats_yaml_data(self):
        """
        获取兼容不同格式的yaml数据
        :return:
        """
        resList = []
        for i in self.get_yaml_data():
            resList.append(i)
        return resList

    @staticmethod
    def _switch():
        # 获取数据库开关
        switch = GetCaseData(ConfigHandler.config_path).\
            get_yaml_data()['MySqlDB']["switch"]
        return switch

    def get_yaml_case_data(self):
        """
        获取测试用例数据, 转换成指定数据格式
        :return:
        """
        try:
            resList = []

            for i in self.get_yaml_data():
                # 正则替换相关数据
                reData = regular(str(i))
                redata = eval(reData)
                resList.append(redata)
            return resList
        except yaml.scanner.ScannerError:
            raise "yaml格式不正确"


if __name__ == '__main__':
    pass
