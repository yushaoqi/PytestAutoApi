#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/2/21 17:33
# @Author : 余少琪
import json

from config.setting import ConfigHandler
from tools.yamlControl import GetYamlData
import requests


class WeChatSend:
    """
    企业微信消息通知
    """

    def __init__(self):
        self.weChatData = GetYamlData(ConfigHandler.config_path).get_yaml_data()['WeChat']
        self.curl = self.weChatData['webhook']
        self.headers = {"Content-Type": "application/json"}

    def sendText(self, content, mentioned_mobile_list=None):
        """
        发送文本类型通知
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        :return:
        """
        _DATA = {"msgtype": "text", "text": {"content": content, "mentioned_list": None,
                                             "mentioned_mobile_list": mentioned_mobile_list}}

        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            # 判断手机号码列表中得数据类型，如果为int类型，发送得消息会乱码
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(url=self.curl, json=_DATA, headers=self.headers)
                        print(res.text)
                    else:
                        raise "手机号码必须是字符串类型."
        else:
            raise "手机号码列表必须是list类型."

    def sendMarkDown(self, content):
        """
        发送 MarkDown 类型消息
        :param content: 消息内容，markdown形式
        :return:
        """
        _DATA = {"msgtype": "markdown", "markdown": {"content": content}}
        res = requests.post(url=self.curl, json=_DATA, headers=self.headers)
        if res.json()['errcode'] != 0:
            raise f"企业微信「MarkDown类型」消息发送失败"

    def sendImageText(self, title, description, url, pic):
        """
        发送图文消息
        :param title: 标题，不超过128个字节，超过会自动截断
        :param description: 描述，不超过512个字节，超过会自动截断
        :param url: 点击后跳转的链接
        :param pic: 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。
        :return:
        """
        _DATA = {
            "msgtype": "news", "news": {
                "articles": [{"title": title, "description": description, "url": url, "picurl": pic}]}}
        res = requests.post(url=self.curl, headers=self.headers, json=_DATA)
        if res.json()['errcode'] != 0:
            raise f"企业微信「图文类型」消息发送失败"


if __name__ == '__main__':
    pass
