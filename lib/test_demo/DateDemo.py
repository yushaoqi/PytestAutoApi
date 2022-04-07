#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-03-16 13:07:13
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

        resp = RequestControl().http_request(inData['method'], inData)
        return resp


if __name__ == '__main__':
    path = GetCaseData(ConfigHandler.data_path + r'test_demo\DateDemo.yaml').get_yaml_case_data()[0]
    data = DateDemo().dateDemo(path)
    print(data)