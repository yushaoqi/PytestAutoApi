#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/24 22:08
# @Author : 余少琪
import yaml.scanner
import os
from tools.regularControl import regular


class GetYamlData:

    def __init__(self, file_dir):
        self.fileDir = file_dir

    def get_yaml_data(self) -> dict:
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

    def write_yaml_data(self, key: str, value) -> int:
        """
        更改 yaml 文件中的值
        :param key: 字典的key
        :param value: 写入的值
        :return:
        """
        with open(self.fileDir, 'r', encoding='utf-8') as f:
            # 创建了一个空列表，里面没有元素
            lines = []
            for line in f.readlines():
                if line != '\n':
                    lines.append(line)
            f.close()

        with open(self.fileDir, 'w', encoding='utf-8') as f:
            flag = 0
            for line in lines:
                if key in line and '#' not in line:
                    left_str = line.split(":")[0]
                    newline = "{0}: {1}".format(left_str, value)
                    line = newline
                    f.write('%s\n' % line)
                    flag = 1
                else:
                    f.write('%s' % line)
            f.close()
            return flag


class GetCaseData(GetYamlData):

    def get_different_formats_yaml_data(self) -> list:
        """
        获取兼容不同格式的yaml数据
        :return:
        """
        res_list = []
        for i in self.get_yaml_data():
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """
        获取测试用例数据, 转换成指定数据格式
        :return:
        """
        try:
            res_list = []

            for i in self.get_yaml_data():
                # 正则替换相关数据
                re_data = regular(str(i))
                re_data = eval(re_data)
                res_list.append(re_data)
            return res_list
        except yaml.scanner.ScannerError:
            raise ValueError("yaml格式不正确")
