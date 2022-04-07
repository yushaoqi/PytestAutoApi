#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 16:08
# @Author : 余少琪

from jsonpath import jsonpath
from utils.cacheUtils.cacheControl import Cache
from utils.requestsUtils.requestControl import RequestControl
from Enums.dependentType_enum import DependentType
from Enums.yamlData_enum import YAMLDate


class DependentCase:

    @classmethod
    def get_cache(cls, case_id: str) -> str:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id:
        :return: case_id_01
        """
        _case_data = eval(Cache('case_process').get_cache())[case_id]
        return _case_data

    @classmethod
    def jsonpath_data(cls, obj: dict, expr: str) -> list:
        """
        通过jsonpath提取依赖的数据
        :param obj: 对象信息
        :param expr: jsonpath 方法
        :return: 提取到的内容值,返回是个数组

        对象: {"data": applyID} --> jsonpath提取方法: $.data.data.[0].applyId
        """

        _jsonpath_data = jsonpath(obj, expr)
        # 判断是否正常提取到数据，如未提取到，则抛异常
        if _jsonpath_data is not False:
            return _jsonpath_data
        else:
            raise ValueError(f"jsonpath提取失败！\n 提取的数据: {obj} \n jsonpath规则: {expr}")

    @classmethod
    def url_replace(cls, replace_key: str, jsonpath_dates: dict, jsonpath_data: list, case_data: dict):
        """
        url中的动态参数替换
        :param jsonpath_data: jsonpath 解析出来的数据值
        :param replace_key: 用例中需要替换数据的 replace_key
        :param jsonpath_dates: jsonpath 存放的数据值
        :param case_data: 用例数据
        :return:
        """

        # 如: 一般有些接口的参数在url中,并且没有参数名称, /api/v1/work/spu/approval/spuApplyDetails/{id}
        # 那么可以使用如下方式编写用例, 可以使用 $url_params{}替换,
        # 如/api/v1/work/spu/approval/spuApplyDetails/$url_params{id}

        if "$url_param" in replace_key:
            _url = case_data['url'].replace(replace_key, str(jsonpath_data[0]))
            jsonpath_dates['$.url'] = _url
        else:
            jsonpath_dates[replace_key] = jsonpath_data[0]

    @classmethod
    def is_dependent(cls, case_data: dict) -> [list, bool]:
        """
        判断是否有数据依赖
        :return:
        """

        _dependent_type = case_data[YAMLDate.DEPENDENCE_CASE.value]
        # 判断是否有依赖
        if _dependent_type is True:
            # 读取依赖相关的用例数据
            _dependence_case_dates = case_data[YAMLDate.DEPENDENCE_CASE_DATA.value]
            jsonpath_dates = {}
            # 循环所有需要依赖的数据
            for dependence_case_data in _dependence_case_dates:
                dependent_data = dependence_case_data['dependent_data']
                for i in dependent_data:

                    _case_id = dependence_case_data[YAMLDate.CASE_ID.value]
                    _jsonpath = i[YAMLDate.JSONPATH.value]
                    _request_data = case_data[YAMLDate.DATA.value]
                    _replace_key = i[YAMLDate.REPLACE_KEY.value]

                    # 判断依赖数据类型, 依赖 response 中的数据
                    if i[YAMLDate.DEPENDENT_TYPE.value] == DependentType.RESPONSE.value:
                        res = RequestControl().http_request(cls.get_cache(_case_id))
                        jsonpath_data = cls.jsonpath_data(res[0], _jsonpath)
                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                        jsonpath_data=jsonpath_data, case_data=case_data)

                    # 判断依赖数据类型, 依赖 request 中的数据
                    elif i[YAMLDate.DEPENDENT_TYPE.value] == DependentType.REQUEST.value:
                        jsonpath_data = cls.jsonpath_data(case_data, _jsonpath)
                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                        jsonpath_data=jsonpath_data, case_data=case_data)

                    # 判断依赖数据类型，依赖 sql中的数据
                    elif i[YAMLDate.DEPENDENT_TYPE.value] == DependentType.SQL_DATA.value:
                        res = RequestControl().http_request(cls.get_cache(_case_id))
                        jsonpath_data = cls.jsonpath_data(res[1], _jsonpath)
                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                        jsonpath_data=jsonpath_data, case_data=case_data)
            return jsonpath_dates
        else:
            return False

    @classmethod
    def get_dependent_data(cls, yaml_data: dict) -> None:
        """
        jsonpath 和 依赖的数据,进行替换
        :param yaml_data:
        :return:
        """
        _dependent_data = DependentCase().is_dependent(yaml_data)
        # 判断有依赖
        if _dependent_data is not False:
            for key, value in _dependent_data.items():
                # 通过jsonpath判断出需要替换数据的位置
                _change_data = key.split(".")
                # jsonpath 数据解析
                _new_data = 'yaml_data' + ''
                for i in _change_data:
                    if i == '$':
                        pass
                    elif i[0] == '[' and i[-1] == ']':
                        _new_data += "[" + i[1:-1] + "]"
                    else:
                        _new_data += "[" + "'" + i + "'" + "]"
                # 最终提取到的数据,转换成 yaml_data[xxx][xxx]
                _new_data += ' = value'
                exec(_new_data)