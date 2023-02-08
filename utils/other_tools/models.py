import types
from enum import Enum, unique
from typing import Text, Dict, Callable, Union, Optional, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class NotificationType(Enum):
    """ 自动化通知方式 """
    DEFAULT = 0
    DING_TALK = 1
    WECHAT = 2
    EMAIL = 3
    FEI_SHU = 4


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


def load_module_functions(module) -> Dict[Text, Callable]:
    """ 获取 module中方法的名称和所在的内存地址 """
    module_functions = {}

    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    RESPONSE = 'response'
    REQUEST = 'request'
    SQL_DATA = 'sqlData'
    CACHE = "cache"


class Assert(BaseModel):
    jsonpath: Text
    type: Text
    value: Any
    AssertType: Union[None, Text] = None


class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class DependentCaseData(BaseModel):
    case_id: Text
    # dependent_data: List[DependentData]
    dependent_data: Union[None, List[DependentData]] = None


class ParamPrepare(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Text


class SendRequest(BaseModel):
    dependent_type: Text
    jsonpath: Optional[Text]
    cache_data: Optional[Text]
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class TearDown(BaseModel):
    case_id: Text
    param_prepare: Optional[List["ParamPrepare"]]
    send_request: Optional[List["SendRequest"]]


class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Text
    name: Text


class TestCase(BaseModel):
    url: Text
    method: Text
    detail: Text
    # assert_data: Union[Dict, Text] = Field(..., alias="assert")
    assert_data: Union[Dict, Text]
    headers: Union[None, Dict, Text] = {}
    requestType: Text
    is_run: Union[None, bool, Text] = None
    data: Any = None
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    sql: List = None
    setup_sql: List = None
    status_code: Optional[int] = None
    teardown_sql: Optional[List] = None
    teardown: Union[List["TearDown"], None] = None
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    sleep: Optional[Union[int, float]]


class ResponseData(BaseModel):
    url: Text
    is_run: Union[None, bool, Text]
    detail: Text
    response_data: Text
    request_body: Any
    method: Text
    sql_data: Dict
    yaml_data: "TestCase"
    headers: Dict
    cookie: Dict
    assert_data: Dict
    res_time: Union[int, float]
    status_code: int
    teardown: List["TearDown"] = None
    teardown_sql: Union[None, List]
    body: Any


class DingTalk(BaseModel):
    webhook: Union[Text, None]
    secret: Union[Text, None]


class MySqlDB(BaseModel):
    switch: bool = False
    host: Union[Text, None] = None
    user: Union[Text, None] = None
    password: Union[Text, None] = None
    port: Union[int, None] = 3306


class Webhook(BaseModel):
    webhook: Union[Text, None]


class Email(BaseModel):
    send_user: Union[Text, None]
    email_host: Union[Text, None]
    stamp_key: Union[Text, None]
    # 收件人
    send_list: Union[Text, None]


class Config(BaseModel):
    project_name: Text
    env: Text
    tester_name: Text
    notification_type: int = 0
    excel_report: bool
    ding_talk: "DingTalk"
    mysql_db: "MySqlDB"
    mirror_source: Text
    wechat: "Webhook"
    email: "Email"
    lark: "Webhook"
    real_time_update_test_cases: bool = False
    host: Text
    app_host: Union[Text, None]


@unique
class AllureAttachmentType(Enum):
    """
    allure 报告的文件类型枚举
    """
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"

    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"

    PDF = "pdf"


@unique
class AssertMethod(Enum):
    """断言类型"""
    equals = "=="
    less_than = "lt"
    less_than_or_equals = "le"
    greater_than = "gt"
    greater_than_or_equals = "ge"
    not_equals = "not_eq"
    string_equals = "str_eq"
    length_equals = "len_eq"
    length_greater_than = "len_gt"
    length_greater_than_or_equals = 'len_ge'
    length_less_than = "len_lt"
    length_less_than_or_equals = 'len_le'
    contains = "contains"
    contained_by = 'contained_by'
    startswith = 'startswith'
    endswith = 'endswith'
