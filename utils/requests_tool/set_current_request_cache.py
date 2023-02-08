#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/2 11:30
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : set_current_request_cache
# @describe:
"""
import json
from typing import Text
from jsonpath import jsonpath
from utils.other_tools.exceptions import ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler


class SetCurrentRequestCache:
    """将用例中的请求或者响应内容存入缓存"""

    def __init__(
            self,
            current_request_set_cache,
            request_data,
            response_data
    ):
        self.current_request_set_cache = current_request_set_cache
        self.request_data = {"data": request_data}
        self.response_data = response_data.text

    def set_request_cache(
            self,
            jsonpath_value: Text,
            cache_name: Text) -> None:
        """将接口的请求参数存入缓存"""
        _request_data = jsonpath(
            self.request_data,
            jsonpath_value
        )
        if _request_data is not False:
            CacheHandler.update_cache(cache_name=cache_name, value=_request_data[0])
            # Cache(cache_name).set_caches(_request_data[0])
        else:
            raise ValueNotFoundError(
                "缓存设置失败，程序中未检测到需要缓存的数据。"
                f"请求参数: {self.request_data}"
                f"提取的 jsonpath 内容: {jsonpath_value}"
            )

    def set_response_cache(
            self,
            jsonpath_value: Text,
            cache_name
    ):
        """将响应结果存入缓存"""
        _response_data = jsonpath(json.loads(self.response_data), jsonpath_value)
        if _response_data is not False:
            CacheHandler.update_cache(cache_name=cache_name, value=_response_data[0])
            # Cache(cache_name).set_caches(_response_data[0])
        else:
            raise ValueNotFoundError("缓存设置失败，程序中未检测到需要缓存的数据。"
                                     f"请求参数: {self.response_data}"
                                     f"提取的 jsonpath 内容: {jsonpath_value}")

    def set_caches_main(self):
        """设置缓存"""
        if self.current_request_set_cache is not None:
            for i in self.current_request_set_cache:
                _jsonpath = i.jsonpath
                _cache_name = i.name
                if i.type == 'request':
                    self.set_request_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
                elif i.type == 'response':
                    self.set_response_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
