#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/24 23:28
# @Author : 余少琪

import requests
from tools.logControl import ERROR
from tools.runtimeControl import execution_duration
from tools.mysqlControl import MysqlDB
import allure
from tools.logDecorator import log_decorator
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
    def _check_params(cls, res, data: dict) -> tuple:
        """ 抽离出通用模块，判断request中的一些参数校验 """
        if 'url' and 'data' and 'headers' and 'sql' not in data:
            ERROR.logger.error("请求失败，请检查用例数据中是否缺少必要参数[url, data, headers, sql]")
        else:
            # 判断响应码不等于200时，打印文本格式信息
            if res.status_code != 200:
                return res.text, {"sql": None}, data
            # 判断数据库开关为开启状态，获取数据库的数据，并且返回
            if SqlSwitch() and data['sql'] is not None:
                sql_data = MysqlDB().assert_execution(data['sql'], res.json())
                return res.json(), sql_data, data
            return res.json(), {"sql": None}, data

    @execution_duration(3000)
    @log_decorator(True)
    def _do_request(self, data: dict, method: str, **kwargs) -> tuple:
        """
        request的请求的封装
        :param InData:
        :param kwargs:
        :return:
        """
        # 判断测试数据为字典类型
        if isinstance(data, dict):
            if data['requestType'] == Transmission.JSON:
                res = requests.request(method=method, url=data["url"], json=data['data'],
                                       headers=data['headers'], **kwargs)

            elif data['requestType'] == Transmission.FILE:
                res = requests.request(method=method, url=data["url"], files=data['data'],
                                       headers=data['headers'], **kwargs)

            elif data['requestType'] == Transmission.PARAMS:
                res = requests.request(method=method, url=data["url"], params=data['data'],
                                       headers=data['headers'], **kwargs)

            else:
                res = requests.request(method=method, url=data["url"], data=data['data'],
                                       headers=data['headers'], **kwargs)

            allure.dynamic.title(data['detail'])
            allure_step_no(f"请求URL: {data['url']}")
            allure_step_no(f"请求方式: {data['method']}")
            allure_step("请求头: ", data['headers'])
            allure_step("请求数据: ", data['data'])
            allure_step("预期数据: ", data['resp'])
            allure_step("响应结果: ", res.json())
            allure_step_no(f"响应耗时(s): {res.elapsed.total_seconds()}")

            return self._check_params(res, data)
        else:
            raise TypeError("InData 需要是 dict类型")

    def http_request(self, method, data, **kwargs) -> tuple:
        try:
            if method.upper() == 'POST':
                return self._do_request(data, data['method'], **kwargs)
            elif method.upper() == 'GET':
                return self._do_request(data, data['method'], **kwargs)
            elif method.upper() == 'DELETE':
                return self._do_request(data, data['method'], **kwargs)
            elif method.upper() == 'PUT':
                return self._do_request(data, data['method'], **kwargs)
            else:
                raise TypeError(f"请求异常,检查yml文件method")
        except Exception:
            raise


if __name__ == '__main__':
    pass
