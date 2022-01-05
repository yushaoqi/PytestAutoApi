#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021-12-26 20:11:48
# @Author : 余少琪


from tools.requestControl import RequestControl
from tools.yamlControl import GetCaseData


class TestDemo(object):
    @staticmethod
    def Demo(inData):
        """
        测试的接口
        :param inData:
        :return:
        """

        resp = RequestControl().HttpRequest(inData['method'], inData)
        return resp


if __name__ == '__main__':
    path = GetCaseData(r"C:\Users\hzxy\PycharmProjects\py_auto_demo\data\TestDemo.yaml").get_yaml_case_data()[0]
    data = TestDemo().Demo(path)
    print(data)
        