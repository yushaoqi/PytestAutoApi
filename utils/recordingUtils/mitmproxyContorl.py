#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:46
# @Author : 余少琪

import mitmproxy.http
from mitmproxy import ctx
from ruamel import yaml
import os
from typing import Any, Union
from urllib.parse import parse_qs, urlparse


class Counter:
    """
    代理录制，基于 mitmproxy 库拦截获取网络请求
    将接口请求数据转换成 yaml 测试用例
    参考资料: https://blog.wolfogre.com/posts/usage-of-mitmproxy/
    """

    def __init__(self, filter_url: list, filename: str = './data/proxy_data.yaml'):
        self.num = 0
        self.file = filename
        self.counter = 1
        # 需要过滤的 url
        self.url = filter_url

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        mitmproxy抓包处理响应，在这里汇总需要数据, 过滤 包含指定url，并且响应格式是 json的
        :param flow:
        :return:
        """
        # 存放需要过滤的接口
        filter_url_type = ['.css', '.js', '.map', '.ico', '.png', '.woff', '.map3', '.jpeg']
        url = flow.request.url
        # 判断过滤掉含 filter_url_type 中后缀的 url
        if any(i in url for i in filter_url_type) is False:
            # 存放测试用例
            if self.filter_url(url):

                data = self.data_handle(flow.request.text)
                method = flow.request.method
                header = self.token_handle(flow.request.headers)
                response = flow.response.text
                case_id = self.get_case_id(url) + str(self.counter)
                cases = {
                    case_id: {
                        "host": self.host_handle(url, types='host'),
                        "url": self.host_handle(url),
                        "method": method,
                        "detail": None,
                        "headers": header,
                        'requestType': self.request_type_handler(method),
                        "is_run": True,
                        "data": data,
                        "dependence_case": None,
                        "dependence_case_data": None,
                        "assert": self.response_code_handler(response),
                        "sql": None
                    }

                }
                # 判断如果请求参数时拼接在url中，提取url中参数，转换成字典
                if "?" in url:
                    cases[case_id]['url'] = self.get_url_handler(url)[1]
                    cases[case_id]['data'] = self.get_url_handler(url)[0]

                # 处理请求头中需要的数据
                self.request_headers(flow.request.headers, cases)

                ctx.log.info("=" * 100)
                ctx.log.info(cases)

                # 判断文件不存在则创建文件
                try:
                    self.yaml_cases(cases)
                except FileNotFoundError:
                    os.makedirs(self.file)
                self.counter += 1

    @classmethod
    def get_case_id(cls, url: str) -> str:
        """
        通过url，提取对应的user_id
        :param url:
        :return:
        """
        _url_path = str(url).split('?')[0]
        # 通过url中的接口地址，最后一个参数，作为case_id的名称
        _url = _url_path.split('/')
        return _url[-1]

    def filter_url(self, url: str) -> bool:
        """过滤url"""
        for i in self.url:
            if i in url:
                return True
        return False

    @classmethod
    def response_code_handler(cls, response) -> Union[dict, None]:
        # 处理接口响应，默认断言数据为code码，如果接口没有code码，则返回None
        try:
            data = cls.data_handle(response)
            return {"code": {"jsonpath": "$.code", "type": "==",
                             "value": data['code'], "AssertType": None}}
        except KeyError:
            return None
        except NameError:
            return None

    @classmethod
    def request_type_handler(cls, method: str) -> str:
        # 处理请求类型，有params、json、file,需要根据公司的业务情况自己调整
        if method == 'GET':
            # 如我们公司只有get请求是prams，其他都是json的
            return 'params'
        else:
            return 'json'

    @classmethod
    def request_headers(cls, headers, cases: dict) -> dict:
        # 公司业务: 请求头中包含了 X-Shop-Id、X-Sub-Biz-Type, 其他项目可注释此段代码
        if 'X-Shop-Id' in headers:
            cases['headers']['X-Shop-Id'] = headers['X-Shop-Id']
        if 'X-Biz-Type' in headers:
            cases['headers']['X-Biz-Type'] = headers['X-Biz-Type']
        if 'X-Sub-Biz-Type' in headers:
            cases['headers']['X-Sub-Biz-Type'] = headers['X-Sub-Biz-Type']
        return cases

    @classmethod
    def data_handle(cls, dict_str) -> Any:
        # 处理接口请求、响应的数据，如null、true格式问题
        try:
            if dict_str != "":
                if 'null' in dict_str:
                    dict_str = dict_str.replace('null', 'None')
                if 'true' in dict_str:
                    dict_str = dict_str.replace('true', 'True')
                if 'false' in dict_str:
                    dict_str = dict_str.replace('false', 'False')
                dict_str = eval(dict_str)
            if dict_str == "":
                dict_str = None
            return dict_str
        except Exception:
            raise

    @classmethod
    def token_handle(cls, header) -> dict:
        # token 处理
        headers = {}
        if 'token' in header:
            headers['token'] = header['token']
        # Content-Type
        headers['Content-Type'] = header['Content-Type']
        return headers

    def host_handle(self, url: str, types='url') -> str:
        """
        解析 url
        :param types: 获取类型: url、host
        :param url: https://xxxx.test.xxxx.com/#/goods/listShop
        :return: 最终返回 ${{MerchantHost}}/#/goods/listShop
        """
        for i in self.url:
            host = None
            if "merchant.test.feng-go.com" in i:
                host = "${{MerchantHost}}"
            elif "cms.test.hunshehui.cn" in i:
                host = "${{CMSHost}}"
            elif "work.test.feng-go.com" in i:
                host = "${{WorkHost}}"
            if types == 'host':
                # 返回域名
                return host
            elif types == 'url':
                # 返回接口地址
                return url.split(i)[-1]

    def yaml_cases(self, data: dict) -> None:
        """
        写入 yaml 数据
        :param data: 测试用例数据
        :return:
        """
        with open(self.file, "a", encoding="utf-8") as f:
            yaml.dump(data, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)

    @classmethod
    def get_url_handler(cls, url: str) -> tuple:
        """
        将 url 中的参数 转换成字典
        :param url: /trade?tradeNo=&outTradeId=11
        :return: {“outTradeId”: 11}
        """
        query = urlparse(url).query
        # 将字符串转换为字典
        params = parse_qs(query)
        # 所得的字典的value都是以列表的形式存在，如请求url中的参数值为空，则字典中不会有该参数
        result = {key: params[key][0] for key in params}
        url = url[0:url.rfind('?')]
        return result, url


# 1、本机需要设置代理，默认端口为: 8080
# 2、控制台输入 mitmweb -s .\utils\recordingUtils\mitmproxyControl.py - p 8888命令开启代理模式进行录制


addons = [
    Counter(["http://work.test.feng-go.com", "http://cms.test.hunshehui.cn/"])
]
