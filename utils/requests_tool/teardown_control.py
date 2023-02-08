#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/23 14:22
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : teardownControl
# @describe: 请求后置处理
"""
import ast
import json
from typing import Dict, Text
from jsonpath import jsonpath
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import cache_regular, sql_regular, regular
from utils.other_tools.jsonpath_date_replace import jsonpath_replace
from utils.mysql_tool.mysql_control import MysqlDB
from utils.logging_tool.log_control import WARNING
from utils.other_tools.models import ResponseData, TearDown, SendRequest, ParamPrepare
from utils.other_tools.exceptions import JsonpathExtractionFailed, ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler
from utils import config


class TearDownHandler:
    """ 处理yaml格式后置请求 """
    def __init__(self, res: "ResponseData"):
        self._res = res

    @classmethod
    def jsonpath_replace_data(
            cls,
            replace_key: Text,
            replace_value: Dict) -> Text:

        """ 通过jsonpath判断出需要替换数据的位置 """
        _change_data = replace_key.split(".")
        # jsonpath 数据解析
        _new_data = jsonpath_replace(
            change_data=_change_data,
            key_name='_teardown_case',
            data_switch=False
        )

        if not isinstance(replace_value, str):
            _new_data += f" = {replace_value}"
        # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
        else:
            _new_data += f" = '{replace_value}'"
        return _new_data

    @classmethod
    def get_cache_name(
            cls,
            replace_key: Text,
            resp_case_data: Dict) -> None:
        """
        获取缓存名称，并且讲提取到的数据写入缓存
        """
        if "$set_cache{" in replace_key and "}" in replace_key:
            start_index = replace_key.index("$set_cache{")
            end_index = replace_key.index("}", start_index)
            old_value = replace_key[start_index:end_index + 2]
            cache_name = old_value[11:old_value.index("}")]
            CacheHandler.update_cache(cache_name=cache_name, value=resp_case_data)
            # Cache(cache_name).set_caches(resp_case_data)

    @classmethod
    def regular_testcase(cls, teardown_case: Dict) -> Dict:
        """处理测试用例中的动态数据"""
        test_case = regular(str(teardown_case))
        test_case = ast.literal_eval(cache_regular(str(test_case)))
        return test_case

    @classmethod
    def teardown_http_requests(cls, teardown_case: Dict) -> "ResponseData":
        """
        发送后置请求
        @param teardown_case: 后置用例
        @return:
        """

        test_case = cls.regular_testcase(teardown_case)
        res = RequestControl(test_case).http_request(
            dependent_switch=False
        )
        return res

    def dependent_type_response(
            self,
            teardown_case_data: "SendRequest",
            resp_data: Dict) -> Text:
        """
        判断依赖类型为当前执行用例响应内容
        :param : teardown_case_data: teardown中的用例内容
        :param : resp_data: 需要替换的内容
        :return:
        """
        _replace_key = teardown_case_data.replace_key
        _response_dependent = jsonpath(
            obj=resp_data,
            expr=teardown_case_data.jsonpath
        )
        # 如果提取到数据，则进行下一步
        if _response_dependent is not False:
            _resp_case_data = _response_dependent[0]
            data = self.jsonpath_replace_data(
                replace_key=_replace_key,
                replace_value=_resp_case_data
            )
        else:
            raise JsonpathExtractionFailed(
                f"jsonpath提取失败，替换内容: {resp_data} \n"
                f"jsonpath: {teardown_case_data.jsonpath}"
            )
        return data

    def dependent_type_request(
            self,
            teardown_case_data: Dict,
            request_data: Dict) -> None:
        """
        判断依赖类型为请求内容
        :param : teardown_case_data: teardown中的用例内容
        :param : request_data: 需要替换的内容
        :return:
        """
        try:
            _request_set_value = teardown_case_data['set_value']
            _request_dependent = jsonpath(
                obj=request_data,
                expr=teardown_case_data['jsonpath']
            )
            if _request_dependent is not False:
                _request_case_data = _request_dependent[0]
                self.get_cache_name(
                    replace_key=_request_set_value,
                    resp_case_data=_request_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath提取失败，替换内容: {request_data} \n"
                    f"jsonpath: {teardown_case_data['jsonpath']}"
                )
        except KeyError as exc:
            raise ValueNotFoundError("teardown中缺少set_value参数，请检查用例是否正确") from exc

    def dependent_self_response(
            self,
            teardown_case_data: "ParamPrepare",
            res: Dict,
            resp_data: Dict) -> None:
        """
        判断依赖类型为依赖用例ID自己响应的内容
        :param : teardown_case_data: teardown中的用例内容
        :param : resp_data: 需要替换的内容
        :param : res: 接口响应的内容
        :return:
        """
        try:
            _set_value = teardown_case_data.set_cache
            _response_dependent = jsonpath(
                obj=res,
                expr=teardown_case_data.jsonpath
            )
            # 如果提取到数据，则进行下一步
            if _response_dependent is not False:
                _resp_case_data = _response_dependent[0]
                # 拿到 set_cache 然后将数据写入缓存
                # Cache(_set_value).set_caches(_resp_case_data)
                CacheHandler.update_cache(cache_name=_set_value, value=_resp_case_data)
                self.get_cache_name(
                    replace_key=_set_value,
                    resp_case_data=_resp_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath提取失败，替换内容: {resp_data} \n"
                    f"jsonpath: {teardown_case_data.jsonpath}")
        except KeyError as exc:
            raise ValueNotFoundError("teardown中缺少set_cache参数，请检查用例是否正确") from exc

    @classmethod
    def dependent_type_cache(cls, teardown_case: "SendRequest") -> Text:
        """
        判断依赖类型为从缓存中处理
        :param : teardown_case_data: teardown中的用例内容
        :return:
        """
        if teardown_case.dependent_type == 'cache':
            _cache_name = teardown_case.cache_data
            _replace_key = teardown_case.replace_key
            # 通过jsonpath判断出需要替换数据的位置
            _change_data = _replace_key.split(".")
            _new_data = jsonpath_replace(
                change_data=_change_data,
                key_name='_teardown_case',
                data_switch=False
            )
            # jsonpath 数据解析
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in _cache_name for i in value_types) is True:
                # _cache_data = Cache(_cache_name.split(':')[1]).get_cache()
                _cache_data = CacheHandler.get_cache(_cache_name.split(':')[1])
                _new_data += f" = {_cache_data}"

            # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
            else:
                # _cache_data = Cache(_cache_name).get_cache()
                _cache_data = CacheHandler.get_cache(_cache_name)
                _new_data += f" = '{_cache_data}'"

            return _new_data

    def send_request_handler(
            self, data: "TearDown",
            resp_data: Dict,
            request_data: Dict
    ) -> None:
        """
        后置请求处理
        @return:
        """
        _send_request = data.send_request
        _case_id = data.case_id
        # _teardown_case = ast.literal_eval(Cache('case_process').get_cache())[_case_id]
        _teardown_case = CacheHandler.get_cache(_case_id)
        for i in _send_request:
            if i.dependent_type == 'cache':
                exec(self.dependent_type_cache(teardown_case=i))
            # 判断从响应内容提取数据
            if i.dependent_type == 'response':
                exec(
                    self.dependent_type_response(
                        teardown_case_data=i,
                        resp_data=resp_data)
                )
            # 判断请求中的数据
            elif i.dependent_type == 'request':
                self.dependent_type_request(
                    teardown_case_data=i,
                    request_data=request_data
                )

        test_case = self.regular_testcase(_teardown_case)
        self.teardown_http_requests(test_case)

    def param_prepare_request_handler(
            self,
            data: "TearDown",
            resp_data: Dict) -> None:
        """
        前置请求处理
        @param data:
        @param resp_data:
        @return:
        """
        _case_id = data.case_id
        # _teardown_case = ast.literal_eval(Cache('case_process').get_cache())[_case_id]
        _teardown_case = CacheHandler.get_cache(_case_id)
        _param_prepare = data.param_prepare
        res = self.teardown_http_requests(_teardown_case)
        for i in _param_prepare:
            # 判断请求类型为自己,拿到当前case_id自己的响应
            if i.dependent_type == 'self_response':
                self.dependent_self_response(
                    teardown_case_data=i,
                    resp_data=resp_data,
                    res=json.loads(res.response_data)
                )

    def teardown_handle(self) -> None:
        """
        为什么在这里需要单独区分 param_prepare 和 send_request
        假设此时我们有用例A，teardown中我们需要执行用例B

        那么考虑用户可能需要获取获取teardown的用例B的响应内容，也有可能需要获取用例A的响应内容，
        因此我们这里需要通过关键词去做区分。这里需要考虑到，假设我们需要拿到B用例的响应，那么就需要先发送请求然后在拿到响应数据

        那如果我们需要拿到A接口的响应，此时我们就不需要在额外发送请求了，因此我们需要区分一个是前置准备param_prepare，
        一个是发送请求send_request
        @return:
        """
        # 拿到用例信息
        _teardown_data = self._res.teardown
        # 获取接口的响应内容
        _resp_data = self._res.response_data
        # 获取接口的请求参数
        _request_data = self._res.yaml_data.data
        # 判断如果没有 teardown
        if _teardown_data is not None:
            # 循环 teardown中的接口
            for _data in _teardown_data:
                if _data.param_prepare is not None:
                    self.param_prepare_request_handler(
                        data=_data,
                        resp_data=json.loads(_resp_data)
                    )
                elif _data.send_request is not None:
                    self.send_request_handler(
                        data=_data,
                        request_data=_request_data,
                        resp_data=json.loads(_resp_data)
                    )
        self.teardown_sql()

    def teardown_sql(self) -> None:
        """处理后置sql"""

        sql_data = self._res.teardown_sql
        _response_data = self._res.response_data
        if sql_data is not None:
            for i in sql_data:
                if config.mysql_db.switch:
                    _sql_data = sql_regular(value=i, res=json.loads(_response_data))
                    MysqlDB().execute(cache_regular(_sql_data))
                else:
                    WARNING.logger.warning("程序中检查到您数据库开关为关闭状态，已为您跳过删除sql: %s", i)
