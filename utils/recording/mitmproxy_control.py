#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:46
# @Author : 余少琪
"""
from urllib.parse import parse_qs, urlparse
from typing import Any, Union, Text, List, Dict, Tuple
import ast
import os
import mitmproxy.http
from mitmproxy import ctx
from ruamel import yaml


class Counter:
    """
    代理录制，基于 mitmproxy 库拦截获取网络请求
    将接口请求数据转换成 yaml 测试用例
    参考资料: https://blog.wolfogre.com/posts/usage-of-mitmproxy/
    """

    def __init__(self, filter_url: List, filename: Text = './data/proxy_data.yaml'):
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
        filter_url_type = ['.css', '.js', '.map', '.ico', '.png', '.woff', '.map3', '.jpeg', '.jpg']
        url = flow.request.url
        ctx.log.info("=" * 100)
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
                        "host": self.host_handle(url),
                        "url": self.url_path_handle(url),
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

                ctx.log.info("=" * 100)
                ctx.log.info(cases)

                # 判断文件不存在则创建文件
                try:
                    self.yaml_cases(cases)
                except FileNotFoundError:
                    os.makedirs(self.file)
                self.counter += 1

    @classmethod
    def get_case_id(cls, url: Text) -> Text:
        """
        通过url，提取对应的user_id
        :param url:
        :return:
        """
        _url_path = str(url).split('?')[0]
        # 通过url中的接口地址，最后一个参数，作为case_id的名称
        _url = _url_path.split('/')
        return _url[-1]

    def filter_url(self, url: Text) -> bool:
        """过滤url"""
        for i in self.url:
            # 判断当前拦截的url地址，是否是addons中配置的host
            if i in url:
                # 如果是，则返回True
                return True
        # 否则返回 False
        return False

    @classmethod
    def response_code_handler(cls, response) -> Union[Dict, None]:
        """
        处理接口响应，默认断言数据为code码，如果接口没有code码，则返回None
        @param response:
        @return:
        """
        try:
            data = cls.data_handle(response)
            return {"code": {"jsonpath": "$.code", "type": "==",
                             "value": data['code'], "AssertType": None}}
        except KeyError:
            return None
        except NameError:
            return None

    @classmethod
    def request_type_handler(cls, method: Text) -> Text:
        """ 处理请求类型，有params、json、file,需要根据公司的业务情况自己调整 """
        if method == 'GET':
            # 如我们公司只有get请求是prams，其他都是json的
            return 'params'
        return 'json'

    @classmethod
    def data_handle(cls, dict_str) -> Any:
        """处理接口请求、响应的数据，如null、true格式问题"""
        try:
            if dict_str != "":
                if 'null' in dict_str:
                    dict_str = dict_str.replace('null', 'None')
                if 'true' in dict_str:
                    dict_str = dict_str.replace('true', 'True')
                if 'false' in dict_str:
                    dict_str = dict_str.replace('false', 'False')
                dict_str = ast.literal_eval(dict_str)
            if dict_str == "":
                dict_str = None
            return dict_str
        except Exception as exc:
            raise exc

    @classmethod
    def token_handle(cls, header) -> Dict:
        """
        提取请求头参数
        :param header:
        :return:
        """
        # 这里是将所有请求头的数据，全部都拦截出来了
        # 如果公司只需要部分参数，可以在这里加判断过滤
        headers = {}
        for key, value in header.items():
            headers[key] = value
        return headers

    def host_handle(self, url: Text) -> Tuple:
        """
        解析 url
        :param url: https://xxxx.test.xxxx.com/#/goods/listShop
        :return: https://xxxx.test.xxxx.com/
        """
        host = None
        # 循环遍历需要过滤的hosts数据
        for i in self.url:
            # 这里主要是判断，如果我们conf.py中有配置这个域名，则用例中展示 ”${{host}}“，动态获取用例host
            # 大家可以在这里改成自己公司的host地址
            if 'https://www.wanandroid.com' in url:
                host = '${{host}}'
            elif i in url:
                host = i
        return host

    def url_path_handle(self, url: Text):
        """
        解析 url_path
        :param url: https://xxxx.test.xxxx.com/shopList/json
        :return: /shopList/json
        """
        url_path = None
        # 循环需要拦截的域名
        for path in self.url:
            if path in url:
                url_path = url.split(path)[-1]
        return url_path

    def yaml_cases(self, data: Dict) -> None:
        """
        写入 yaml 数据
        :param data: 测试用例数据
        :return:
        """
        with open(self.file, "a", encoding="utf-8") as file:
            yaml.dump(data, file, Dumper=yaml.RoundTripDumper, allow_unicode=True)
            file.write('\n')

    def get_url_handler(self, url: Text) -> Tuple:
        """
        将 url 中的参数 转换成字典
        :param url: /trade?tradeNo=&outTradeId=11
        :return: {“outTradeId”: 11}
        """
        result = None
        url_path = None
        for i in self.url:
            if i in url:
                query = urlparse(url).query
                # 将字符串转换为字典
                params = parse_qs(query)
                # 所得的字典的value都是以列表的形式存在，如请求url中的参数值为空，则字典中不会有该参数
                result = {key: params[key][0] for key in params}
                url = url[0:url.rfind('?')]
                url_path = url.split(i)[-1]
        return result, url_path


# 1、本机需要设置代理，默认端口为: 8080
# 2、控制台输入 mitmweb -s .\utils\recording\mitmproxy_control.py - p 8888命令开启代理模式进行录制


addons = [
    Counter(["https://www.wanandroid.com"])
    ]
