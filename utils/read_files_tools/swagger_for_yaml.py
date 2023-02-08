#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/8/11 10:51
# @Author : 余少琪
"""
import json
from jsonpath import jsonpath
from common.setting import ensure_path_sep
from typing import Dict
from ruamel import yaml
import os


class SwaggerForYaml:
    def __init__(self):
        self._data = self.get_swagger_json()

    @classmethod
    def get_swagger_json(cls):
        """
        获取 swagger 中的 json 数据
        :return:
        """
        try:
            with open('./file/test_OpenAPI.json', "r", encoding='utf-8') as f:
                row_data = json.load(f)
                return row_data
        except FileNotFoundError:
            raise FileNotFoundError("文件路径不存在，请重新输入")

    def get_allure_epic(self):
        """ 获取 yaml 用例中的 allure_epic """
        _allure_epic = self._data['info']['title']
        return _allure_epic

    @classmethod
    def get_allure_feature(cls, value):
        """ 获取 yaml 用例中的 allure_feature """
        _allure_feature = value['tags']
        return str(_allure_feature)

    @classmethod
    def get_allure_story(cls, value):
        """ 获取 yaml 用例中的 allure_story """
        _allure_story = value['summary']
        return _allure_story

    @classmethod
    def get_case_id(cls, value):
        """ 获取 case_id """
        _case_id = value.replace("/", "_")
        return "01" + _case_id

    @classmethod
    def get_detail(cls, value):
        _get_detail = value['summary']
        return "测试" + _get_detail

    @classmethod
    def get_request_type(cls, value, headers):
        """ 处理 request_type """
        if jsonpath(obj=value, expr="$.parameters") is not False:
            _parameters = value['parameters']
            if _parameters[0]['in'] == 'query':
                return "params"
            else:
                if 'application/x-www-form-urlencoded' or 'multipart/form-data' in headers:
                    return "data"
                elif 'application/json' in headers:
                    return "json"
                elif 'application/octet-stream' in headers:
                    return "file"
                else:
                    return "data"

    @classmethod
    def get_case_data(cls, value):
        """ 处理 data 数据 """
        _dict = {}
        if jsonpath(obj=value, expr="$.parameters") is not False:
            _parameters = value['parameters']
            for i in _parameters:
                if i['in'] == 'header':
                    ...
                else:
                    _dict[i['name']] = None
        else:
            return None
        return _dict

    @classmethod
    def yaml_cases(cls, data: Dict, file_path: str) -> None:
        """
        写入 yaml 数据
        :param file_path:
        :param data: 测试用例数据
        :return:
        """

        _file_path = ensure_path_sep("\\data\\" + file_path[1:].replace("/", os.sep) + '.yaml')
        _file = _file_path.split(os.sep)[:-1]
        _dir_path = ''
        for i in _file:
            _dir_path += i + os.sep
        try:
            os.makedirs(_dir_path)
        except FileExistsError:
            ...
        with open(_file_path, "a", encoding="utf-8") as file:
            yaml.dump(data, file, Dumper=yaml.RoundTripDumper, allow_unicode=True)
            file.write('\n')

    @classmethod
    def get_headers(cls, value):
        """ 获取请求头 """
        _headers = {}
        if jsonpath(obj=value, expr="$.consumes") is not False:
            _headers = {"Content-Type": value['consumes'][0]}
        if jsonpath(obj=value, expr="$.parameters") is not False:
            for i in value['parameters']:
                if i['in'] == 'header':
                    _headers[i['name']] = None
        else:
            _headers = None
        return _headers

    def write_yaml_handler(self):

        _api_data = self._data['paths']
        for key, value in _api_data.items():
            for k, v in value.items():
                yaml_data = {
                    "case_common": {"allureEpic": self.get_allure_epic(), "allureFeature": self.get_allure_feature(v),
                                    "allureStory": self.get_allure_story(v)},
                    self.get_case_id(key): {
                        "host": "${{host()}}", "url": key, "method": k, "detail": self.get_detail(v),
                        "headers": self.get_headers(v), "requestType": self.get_request_type(v, self.get_headers(v)),
                        "is_run": None, "data": self.get_case_data(v), "dependence_case": False,
                        "assert": {"status_code": 200}, "sql": None}}
                self.yaml_cases(yaml_data, file_path=key)


if __name__ == '__main__':
    SwaggerForYaml().write_yaml_handler()
