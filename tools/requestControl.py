#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/24 23:28
# @Author : 余少琪
import json

import requests
from tools.logControl import ERROR
from tools.runtimeControl import executionDuration
from tools.mysqlControl import MysqlDB
import allure
from tools.logDecorator import logDecorator
from tools import allure_step, allure_step_no, SqlSwitch


class Transmission:
    JSON: str = "json"
    PARAMS: str = "params"
    DATE: str = "date"
    FILE: str = 'file'


class RequestControl:
    """ 封装请求 """

    def __init__(self):
        # TODO 初始化逻辑调整
        pass

    @classmethod
    def _checkParams(cls, res, InData: dict) -> tuple:
        """ 抽离出通用模块，判断request中的一些参数校验 """
        if 'url' and 'data' and 'headers' and 'sql' not in InData:
            ERROR.logger.error("请求失败，请检查用例数据中是否缺少必要参数[url, data, headers, sql]")
        else:
            # 判断响应码不等于200时，打印文本格式信息
            if res.status_code != 200:
                return res.text, {"sql": None}, InData
            # 判断数据库开关为开启状态，获取数据库的数据，并且返回
            if SqlSwitch() and InData['sql'] is not None:
                sqlData = MysqlDB().assert_execution(InData['sql'], res.json())
                return res.json(), sqlData, InData
            return res.json(), {"sql": None}, InData

    @executionDuration(3000)
    @logDecorator(True)
    def _DoRequest(self, InData: dict, method: str, **kwargs) -> tuple:
        """
        request的请求的封装
        :param InData:
        :param kwargs:
        :return:
        """
        # 判断测试数据为字典类型
        if isinstance(InData, dict):
            if InData['requestType'] == Transmission.JSON:
                res = requests.request(method=method, url=InData["url"], json=InData['data'],
                                       headers=InData['headers'], **kwargs)

            elif InData['requestType'] == Transmission.FILE:
                res = requests.request(method=method, url=InData["url"], files=InData['data'],
                                       headers=InData['headers'], **kwargs)

            elif InData['requestType'] == Transmission.PARAMS:
                res = requests.request(method=method, url=InData["url"], params=InData['data'],
                                       headers=InData['headers'], **kwargs)

            else:
                res = requests.request(method=method, url=InData["url"], data=InData['data'],
                                       headers=InData['headers'], **kwargs)

            allure.dynamic.title(InData['detail'])
            allure_step_no(f"请求URL: {InData['url']}")
            allure_step_no(f"请求方式: {InData['method']}")
            allure_step("请求头: ", InData['headers'])
            allure_step("请求数据: ", InData['data'])
            allure_step("预期数据: ", InData['resp'])
            allure_step("响应结果: ", res.json())
            allure_step_no(f"响应耗时(s): {res.elapsed.total_seconds()}")

            return self._checkParams(res, InData)
        else:
            raise TypeError("InData 需要是 dict类型")

    def HttpRequest(self, Method, inData, **kwargs) -> tuple:
        try:
            if Method.upper() == 'POST':
                return self._DoRequest(inData, inData['method'], **kwargs)
            elif Method.upper() == 'GET':
                return self._DoRequest(inData, inData['method'], **kwargs)
            elif Method.upper() == 'DELETE':
                return self._DoRequest(inData, inData['method'], **kwargs)
            elif Method.upper() == 'PUT':
                return self._DoRequest(inData, inData['method'], **kwargs)
            else:
                raise TypeError(f"请求异常,检查yml文件method")
        except Exception:
            raise


if __name__ == '__main__':
    pass
