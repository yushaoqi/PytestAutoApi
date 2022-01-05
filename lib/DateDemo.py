#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-01-05 16:44:47
# @Author : 余少琪


from tools.requestControl import RequestControl
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler


class DateDemo(object):
    @staticmethod
    def dateDemo(inData):
        """
        测试接口
        :param inData:
        :return:
        """

        resp = RequestControl().HttpRequest(inData['method'], inData)
        return resp


if __name__ == '__main__':
    path = GetCaseData(ConfigHandler.data_path + r'DateDemo.yaml').get_yaml_case_data()[0]
    data = DateDemo().dateDemo(path)
    print(data)
        