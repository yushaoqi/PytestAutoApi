"""
# @Time   : 2022/3/28 16:08
# @Author : 余少琪
"""
import ast
import json
from typing import Text, Dict, Union, List
from jsonpath import jsonpath
from utils.requests_tool.request_control import RequestControl
from utils.mysql_tool.mysql_control import SetUpMySQL
from utils.read_files_tools.regular_control import regular, cache_regular
from utils.other_tools.jsonpath_date_replace import jsonpath_replace
from utils.logging_tool.log_control import WARNING
from utils.other_tools.models import DependentType
from utils.other_tools.models import TestCase, DependentCaseData, DependentData
from utils.other_tools.exceptions import ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler
from utils import config


class DependentCase:
    """ 处理依赖相关的业务 """

    def __init__(self, dependent_yaml_case: TestCase):
        self.__yaml_case = dependent_yaml_case

    @classmethod
    def get_cache(cls, case_id: Text) -> Dict:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id:
        :return: case_id_01
        """
        _case_data = CacheHandler.get_cache(case_id)
        return _case_data

    @classmethod
    def jsonpath_data(
            cls,
            obj: Dict,
            expr: Text) -> list:
        """
        通过jsonpath提取依赖的数据
        :param obj: 对象信息
        :param expr: jsonpath 方法
        :return: 提取到的内容值,返回是个数组

        对象: {"data": applyID} --> jsonpath提取方法: $.data.data.[0].applyId
        """

        _jsonpath_data = jsonpath(obj, expr)
        # 判断是否正常提取到数据，如未提取到，则抛异常
        if _jsonpath_data is False:
            raise ValueNotFoundError(
                f"jsonpath提取失败！\n 提取的数据: {obj} \n jsonpath规则: {expr}"
            )
        return _jsonpath_data

    @classmethod
    def set_cache_value(cls, dependent_data: "DependentData") -> Union[Text, None]:
        """
        获取依赖中是否需要将数据存入缓存中
        """
        try:
            return dependent_data.set_cache
        except KeyError:
            return None

    @classmethod
    def replace_key(cls, dependent_data: "DependentData"):
        """ 获取需要替换的内容 """
        try:
            _replace_key = dependent_data.replace_key
            return _replace_key
        except KeyError:
            return None

    def url_replace(
            self,
            replace_key: Text,
            jsonpath_dates: Dict,
            jsonpath_data: list) -> None:
        """
        url中的动态参数替换
        # 如: 一般有些接口的参数在url中,并且没有参数名称, /api/v1/work/spu/approval/spuApplyDetails/{id}
        # 那么可以使用如下方式编写用例, 可以使用 $url_params{}替换,
        # 如/api/v1/work/spu/approval/spuApplyDetails/$url_params{id}
        :param jsonpath_data: jsonpath 解析出来的数据值
        :param replace_key: 用例中需要替换数据的 replace_key
        :param jsonpath_dates: jsonpath 存放的数据值
        :return:
        """

        if "$url_param" in replace_key:
            _url = self.__yaml_case.url.replace(replace_key, str(jsonpath_data[0]))
            jsonpath_dates['$.url'] = _url
        else:
            jsonpath_dates[replace_key] = jsonpath_data[0]

    def _dependent_type_for_sql(
            self,
            setup_sql: List,
            dependence_case_data: "DependentCaseData",
            jsonpath_dates: Dict) -> None:
        """
        判断依赖类型为 sql，程序中的依赖参数从 数据库中提取数据
        @param setup_sql: 前置sql语句
        @param dependence_case_data: 依赖的数据
        @param jsonpath_dates: 依赖相关的用例数据
        @return:
        """
        # 判断依赖数据类型，依赖 sql中的数据
        if setup_sql is not None:
            if config.mysql_db.switch:
                setup_sql = ast.literal_eval(cache_regular(str(setup_sql)))
                sql_data = SetUpMySQL().setup_sql_data(sql=setup_sql)
                dependent_data = dependence_case_data.dependent_data
                for i in dependent_data:
                    _jsonpath = i.jsonpath
                    jsonpath_data = self.jsonpath_data(obj=sql_data, expr=_jsonpath)
                    _set_value = self.set_cache_value(i)
                    _replace_key = self.replace_key(i)
                    if _set_value is not None:
                        CacheHandler.update_cache(cache_name=_set_value, value=jsonpath_data[0])
                        # Cache(_set_value).set_caches(jsonpath_data[0])
                    if _replace_key is not None:
                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                        self.url_replace(
                            replace_key=_replace_key,
                            jsonpath_dates=jsonpath_dates,
                            jsonpath_data=jsonpath_data,
                        )
            else:
                WARNING.logger.warning("检查到数据库开关为关闭状态，请确认配置")

    def dependent_handler(
            self,
            _jsonpath: Text,
            set_value: Text,
            replace_key: Text,
            jsonpath_dates: Dict,
            data: Dict,
            dependent_type: int
    ) -> None:
        """ 处理数据替换 """
        jsonpath_data = self.jsonpath_data(
            data,
            _jsonpath
        )
        if set_value is not None:
            if len(jsonpath_data) > 1:
                CacheHandler.update_cache(cache_name=set_value, value=jsonpath_data)
            else:
                CacheHandler.update_cache(cache_name=set_value, value=jsonpath_data[0])
        if replace_key is not None:
            if dependent_type == 0:
                jsonpath_dates[replace_key] = jsonpath_data[0]
            self.url_replace(replace_key=replace_key, jsonpath_dates=jsonpath_dates,
                             jsonpath_data=jsonpath_data)

    def is_dependent(self) -> Union[Dict, bool]:
        """
        判断是否有数据依赖
        :return:
        """

        # 获取用例中的dependent_type值，判断该用例是否需要执行依赖
        _dependent_type = self.__yaml_case.dependence_case
        # 获取依赖用例数据
        _dependence_case_dates = self.__yaml_case.dependence_case_data
        _setup_sql = self.__yaml_case.setup_sql
        # 判断是否有依赖
        if _dependent_type is True:
            # 读取依赖相关的用例数据
            jsonpath_dates = {}
            # 循环所有需要依赖的数据
            try:
                for dependence_case_data in _dependence_case_dates:
                    _case_id = dependence_case_data.case_id
                    # 判断依赖数据为sql，case_id需要写成self，否则程序中无法获取case_id
                    if _case_id == 'self':
                        self._dependent_type_for_sql(
                            setup_sql=_setup_sql,
                            dependence_case_data=dependence_case_data,
                            jsonpath_dates=jsonpath_dates)
                    else:
                        re_data = regular(str(self.get_cache(_case_id)))
                        re_data = ast.literal_eval(cache_regular(str(re_data)))
                        res = RequestControl(re_data).http_request()
                        if dependence_case_data.dependent_data is not None:
                            dependent_data = dependence_case_data.dependent_data
                            for i in dependent_data:

                                _case_id = dependence_case_data.case_id
                                _jsonpath = i.jsonpath
                                _request_data = self.__yaml_case.data
                                _replace_key = self.replace_key(i)
                                _set_value = self.set_cache_value(i)
                                # 判断依赖数据类型, 依赖 response 中的数据
                                if i.dependent_type == DependentType.RESPONSE.value:
                                    self.dependent_handler(
                                        data=json.loads(res.response_data),
                                        _jsonpath=_jsonpath,
                                        set_value=_set_value,
                                        replace_key=_replace_key,
                                        jsonpath_dates=jsonpath_dates,
                                        dependent_type=0
                                    )

                                # 判断依赖数据类型, 依赖 request 中的数据
                                elif i.dependent_type == DependentType.REQUEST.value:
                                    self.dependent_handler(
                                        data=res.body,
                                        _jsonpath=_jsonpath,
                                        set_value=_set_value,
                                        replace_key=_replace_key,
                                        jsonpath_dates=jsonpath_dates,
                                        dependent_type=1
                                    )

                                else:
                                    raise ValueError(
                                        "依赖的dependent_type不正确，只支持request、response、sql依赖\n"
                                        f"当前填写内容: {i.dependent_type}"
                                    )
                return jsonpath_dates
            except KeyError as exc:
                # pass
                raise ValueNotFoundError(
                    f"dependence_case_data依赖用例中，未找到 {exc} 参数，请检查是否填写"
                    f"如已填写，请检查是否存在yaml缩进问题"
                ) from exc
            except TypeError as exc:
                raise ValueNotFoundError(
                    "dependence_case_data下的所有内容均不能为空！"
                    "请检查相关数据是否填写，如已填写，请检查缩进问题"
                ) from exc
        else:
            return False

    def get_dependent_data(self) -> None:
        """
        jsonpath 和 依赖的数据,进行替换
        :return:
        """
        _dependent_data = DependentCase(self.__yaml_case).is_dependent()
        _new_data = None
        # 判断有依赖
        if _dependent_data is not None and _dependent_data is not False:
            # if _dependent_data is not False:
            for key, value in _dependent_data.items():
                # 通过jsonpath判断出需要替换数据的位置
                _change_data = key.split(".")
                # jsonpath 数据解析
                # 不要删 这个yaml_case
                yaml_case = self.__yaml_case
                _new_data = jsonpath_replace(change_data=_change_data, key_name='yaml_case')
                # 最终提取到的数据,转换成 __yaml_case.data
                _new_data += ' = ' + str(value)
                exec(_new_data)
