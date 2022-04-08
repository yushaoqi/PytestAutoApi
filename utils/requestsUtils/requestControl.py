#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 12:52
# @Author : 余少琪

import random
import allure
import requests
from typing import Any
from utils import sql_switch
from requests_toolbelt import MultipartEncoder
from utils.logUtils.logDecoratorl import log_decorator
from utils.mysqlUtils.mysqlControl import MysqlDB
from Enums.requestType_enum import RequestType
from Enums.yamlData_enum import YAMLDate
from config.setting import ConfigHandler
from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.runTimeDecoratorl import execution_duration
from utils.otherUtils.allureDate.allure_tools import allure_step, allure_step_no, allure_attach


class RequestControl:
    """ 封装请求 """

    @classmethod
    def _check_params(cls, response, yaml_data) -> Any:
        """ 抽离出通用模块，判断request中的一些参数校验 """
        # 判断响应码不等于200时，打印文本格式信息
        if response.status_code != 200:
            return response.text, {"sql": None}, yaml_data
            # 判断 sql 不是空的话，获取数据库的数据，并且返回
        if sql_switch() and yaml_data['sql'] is not None:
            sql_data = MysqlDB().assert_execution(sql=yaml_data['sql'], resp=response.json())
            return response.json(), sql_data, yaml_data
        return response.json(), {"sql": None}, yaml_data

    @classmethod
    def case_token(cls, header) -> None:
        try:
            # 判断用例是否依赖token
            _token = header['token']
            # 如果依赖则从缓存中读取对应得token信息
            try:
                # 判断如果没有缓存数据，则直接取用例中的数据
                cache = Cache(_token).get_cache()
                header['token'] = cache
            except FileNotFoundError:
                pass
        except KeyError:
            pass

    @classmethod
    def upload_file(cls, yaml_data):
        # 处理上传多个文件的情况
        _files = []
        file_data = {}
        for key, value in yaml_data[YAMLDate.DATA.value]['file'].items():
            file_path = ConfigHandler.file_path + value
            file_data[key] = (value, open(file_path, 'rb'), 'application/octet-stream')
            _files.append(file_data)
            # allure中展示该附件
            allure_attach(source=file_path, name=value, extension=value)
        # 兼容就要上传文件，又要上传其他类型参数
        try:
            for key, value in yaml_data[YAMLDate.DATA.value]['data'].items():
                file_data[key] = value
        except KeyError:
            pass

        multipart = MultipartEncoder(
            fields=file_data,  # 字典格式
            boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1)))
        )

        yaml_data[YAMLDate.HEADER.value]['Content-Type'] = multipart.content_type

        try:
            params = yaml_data[YAMLDate.DATA.value]['params']
        except KeyError:
            params = None
        return multipart, params

    @log_decorator(True)
    @execution_duration(3000)
    def http_request(self, yaml_data, **kwargs):
        from utils.requestsUtils.dependentCase import DependentCase
        _is_run = yaml_data[YAMLDate.IS_RUN.value]
        _method = yaml_data[YAMLDate.METHOD.value]
        _detail = yaml_data[YAMLDate.DETAIL.value]
        _headers = yaml_data[YAMLDate.HEADER.value]
        _requestType = yaml_data[YAMLDate.REQUEST_TYPE.value].upper()
        _data = yaml_data[YAMLDate.DATA.value]
        _sql = yaml_data[YAMLDate.SQL.value]
        _assert = yaml_data[YAMLDate.ASSERT.value]
        _dependent_data = yaml_data[YAMLDate.DEPENDENCE_CASE_DATA.value]
        self.case_token(_headers)
        res = None

        # 判断用例是否执行
        if _is_run is True or _is_run is None:
            # 处理多业务逻辑
            DependentCase().get_dependent_data(yaml_data)

            if _requestType == RequestType.JSON.value:
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], json=_data,
                                       headers=_headers, **kwargs)
            elif _requestType == RequestType.PARAMS.value:

                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], json=_data, headers=_headers,
                                       **kwargs)
            elif _requestType == RequestType.PARAMS.value:
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], params=_data,
                                       headers=_headers, **kwargs)
            # 判断上传文件
            elif _requestType == RequestType.FILE.value:
                multipart = self.upload_file(yaml_data)
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value],
                                       data=multipart[0], params=multipart[1], headers=_headers, **kwargs)

            elif _requestType == RequestType.DATE.value:

                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], data=_data,
                                       headers=_headers, **kwargs)

            elif _requestType == RequestType.DATE.value:
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], data=_data, headers=_headers,
                                       **kwargs)
            allure.dynamic.title(_detail)
            allure_step_no(f"请求URL: {yaml_data[YAMLDate.URL.value]}")
            allure_step_no(f"请求方式: {_method}")
            allure_step("请求头: ", _headers)
            allure_step("请求数据: ", _data)
            allure_step("依赖数据: ", _dependent_data)
            allure_step("预期数据: ", _assert)
            allure_step_no(f"响应耗时(s): {res.elapsed.total_seconds()}")
            if res.status_code != 200:
                allure_step("响应结果: ", res.text)
            else:
                allure_step("响应结果: ", res.json())
            return self._check_params(res, yaml_data)
        else:
            # 用例跳过执行的话，所有数据都返回 False
            return False, False, yaml_data
