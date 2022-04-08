#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/22 13:45
# @Author : 余少琪

from utils import sql_switch
from utils.readFilesUtils.yamlControl import GetCaseData


class CaseData:
    """
    yaml 数据解析, 判断数据填写是否符合规范
    """

    def __init__(self, file_path):
        self.filePath = file_path

    def case_process(self, case_id_switch=None):
        """
        数据清洗之后，返回该 yaml 文件中的所有用例
        :param case_id_switch: 判断数据清洗，是否需要清洗出 case_id, 主要用于兼容用例池中的数据
        :return:
        """
        dates = GetCaseData(self.filePath).get_yaml_case_data()
        case_lists = []
        for key, values in dates.items():
            # 公共配置中的数据，与用例数据不同，需要单独处理
            if key != 'case_common':
                case_date = {
                    'method': self.get_case_method(key, values),
                    'is_run': self.get_is_run(key, values),
                    'url': self.get_case_host(key, values),
                    'detail': self.get_case_detail(values),
                    'headers': self.get_headers(key, values),
                    'requestType': self.get_request_type(key, values),
                    'data': self.get_case_dates(key, values),
                    'dependence_case': self.get_dependence_case(key, values),
                    'dependence_case_data': self.get_dependence_case_data(key, values),
                    "sql": self.get_sql(key, values),
                    "assert": self.get_assert(key, values)
                }
                if case_id_switch is True:
                    case_lists.append({key: case_date})
                else:
                    case_lists.append(case_date)
        return case_lists

    def get_case_host(self, case_id: str, case_data: dict) -> str:
        """
        获取用例的 host
        :return:
        """
        try:
            _url = case_data['url']
            _host = case_data['host']
            if _url is None or _host is None:
                raise ValueError(f"用例中的 url 或者 host 不能为空！\n 用例ID: {case_id} \n 用例路径: {self.filePath}")
            else:
                return _host + _url
        except KeyError:
            raise KeyError(f"用例中未找到 host或url. 用例ID: {case_id}")

    def get_case_method(self, case_id: str, case_data: dict) -> str:
        """
        获取用例的请求方式：GET/POST/PUT/DELETE
        :return:
        """
        try:
            _case_method = case_data['method']
            _request_method = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']
            if _case_method.upper() in _request_method:
                return _case_method.upper()
            else:
                raise ValueError(f"method 目前只支持 {_request_method} 请求方式，如需新增请联系管理员. "
                                 f"{self.raise_value_error(data_name='请求方式', case_id=case_id, detail=_case_method)}")

        except AttributeError:
            raise ValueError(f"method 目前只支持 { ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']} 请求方式，"
                             f"如需新增请联系管理员！ "
                             f"{self.raise_value_error(data_name='请求方式', case_id=case_id, detail=case_data['method'])}")
        except KeyError:
            raise KeyError(f"用例中未找到请求方式 method. 用例ID: {case_id}")

    @classmethod
    def get_case_detail(cls, case_data: dict) -> str:
        """
        获取用例描述
        :return:
        """
        try:
            return case_data['detail']
        except KeyError:
            raise KeyError(f"用例中未找到用例描述 detail. 用例ID: {case_data['detail']}")

    @classmethod
    def get_headers(cls, case_id: str, case_data: dict) -> dict:
        """
        胡求用例请求头中的信息
        :return:
        """
        try:
            _header = case_data['headers']
            return _header
        except KeyError:
            raise KeyError(f"用例中未找到请求头 headers. 用例ID: {case_id}")

    def raise_value_error(self, data_name: str, case_id: str, detail: [str, list, dict]):
        """
        所有用例填写不规范的异常提示
        :param data_name: 参数名称
        :param case_id: 用例ID
        :param detail: 参数内容
        :return:
        """
        detail = f"用例中的 {data_name} 填写不正确！\n 用例ID: {case_id} \n 用例路径: {self.filePath}\n" \
                 f"当前填写的内容: {detail}"

        return detail

    def get_request_type(self, case_id: str, case_data: dict) -> str:
        """
        获取请求类型，params、data、json
        :return:
        """

        _types = ['JSON', 'PARAMS', 'FILE', 'DATE']

        try:
            _request_type = case_data['requestType']
            # 判断用户填写的 requestType是否符合规范
            if _request_type.upper() in _types:
                return _request_type.upper()
            else:
                raise ValueError(self.raise_value_error(data_name='requestType', case_id=case_id, detail=_request_type))
        # 异常捕捉
        except AttributeError:
            raise ValueError(self.raise_value_error(data_name='requestType',
                                                    case_id=case_id, detail=case_data['requestType']))
        except KeyError:
            raise KeyError(f"用例中未找到 requestType. 用例ID: {case_id}")

    @classmethod
    def get_is_run(cls, case_id: str, case_data: dict) -> str:
        """
        获取执行状态, 为 true 或者 None 都会执行
        :return:
        """
        try:
            return case_data['is_run']
        except KeyError:
            raise KeyError(f"用例中未找到 is_run. 用例ID: {case_id}")

    @classmethod
    def get_dependence_case(cls, case_id: str, case_data: dict) -> dict:
        """
        获取是否依赖的用例
        :return:
        """
        try:
            _dependence_case = case_data['dependence_case']
            return _dependence_case
        except KeyError:
            raise KeyError(f"用例中未找到 dependence_case. 用例ID: {case_id}")

    @classmethod
    def get_dependence_case_data(cls, case_id: str, case_data: dict) -> str:
        """
        获取依赖的用例
        :return:
        """
        try:
            _dependence_case_data = case_data['dependence_case_data']
            return _dependence_case_data
        except KeyError:
            raise KeyError(f"用例中未找到 dependence_case. 用例ID: {case_id}")

    @classmethod
    def get_case_dates(cls, case_id: str, case_data: dict) -> dict:
        """
        获取请求数据
        :param case_id:
        :param case_data:
        :return:
        """
        try:
            _dates = case_data['data']
            return _dates
        except KeyError:
            raise KeyError(f"用例中未找到 data 参数. 用例ID: {case_id}")

    def get_assert(self, case_id: str, case_data: dict):
        """
        获取需要断言的数据
        :return:
        """
        try:
            _assert = case_data['assert']
            if _assert is None:
                raise self.raise_value_error(data_name="assert", case_id=case_id, detail=_assert)
            return case_data['assert']
        except KeyError:
            raise KeyError(f"用例中未找到 assert 参数. 用例ID: {case_id}")

    @classmethod
    def get_sql(cls, case_id: str, case_data: dict):
        """
        获取测试用例中的sql
        :return:
        """
        try:
            _sql = case_data['sql']
            # 判断数据库开关为开启状态，并且sql不为空
            if sql_switch() and _sql is not None:
                return case_data['sql']
            else:
                return None
        except KeyError:
            raise KeyError(f"用例中未找到 sql 参数. 用例ID: {case_id}")
