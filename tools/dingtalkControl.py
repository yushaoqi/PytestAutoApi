#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 13:15
# @Author : 余少琪

import base64
import hashlib
import hmac
import time
import urllib.parse
from tools.yamlControl import GetYamlData
from dingtalkchatbot.chatbot import DingtalkChatbot, FeedLink
from config.setting import ConfigHandler
from typing import Any
from tools.allureDataControl import CaseCount
from tools.localIpControl import get_host_ip


class DingTalkSendMsg(object):

    def __init__(self):
        self.timeStamp = str(round(time.time() * 1000))
        self.sign = self.get_sign()
        self.devConfig = ConfigHandler()
        # 从yaml文件中获取钉钉配置信息
        self.getDingTalk = GetYamlData(self.devConfig.config_path).get_yaml_data()['DingTalk']

        # 获取 webhook地址
        self.webhook = self.getDingTalk["webhook"] + "&timestamp=" + self.timeStamp + "&sign=" + self.sign
        self.xiaoDing = DingtalkChatbot(self.webhook)
        self.name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]
        self.tester = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TestName']
        self.allureData = CaseCount()
        self.PASS = self.allureData.pass_count()
        self.FAILED = self.allureData.failed_count()
        self.BROKEN = self.allureData.broken_count()
        self.SKIP = self.allureData.skipped_count()
        self.TOTAL = self.allureData.total_count()
        self.RATE = self.allureData.pass_rate()

    def get_sign(self) -> str:
        """
        根据时间戳 + "sign" 生成密钥
        :return:
        """
        secret = GetYamlData(ConfigHandler().config_path).get_yaml_data()['DingTalk']['secret']
        string_to_sign = '{}\n{}'.format(self.timeStamp, secret).encode('utf-8')
        hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    def send_text(self, msg: str, mobiles=None) -> None:
        """
        发送文本信息
        :param msg: 文本内容
        :param mobiles: 艾特用户电话
        :return:
        """
        if not mobiles:
            self.xiaoDing.send_text(msg=msg, is_at_all=True)
        else:
            if isinstance(mobiles, list):
                self.xiaoDing.send_text(msg=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles类型错误 不是list类型.")

    def send_link(self, title: str, text: str, message_url: str, pic_url: str) -> None:
        """
        发送link通知
        :return:
        """
        try:
            self.xiaoDing.send_link(title=title, text=text, message_url=message_url, pic_url=pic_url)
        except Exception:
            raise

    def send_markdown(self, title: str, msg: str, mobiles=None) -> None:
        """

        :param mobiles:
        :param title:
        :param msg:
        markdown 格式
        """

        if mobiles is None:
            self.xiaoDing.send_markdown(title=title, text=msg, is_at_all=True)
        else:
            if isinstance(mobiles, list):
                self.xiaoDing.send_markdown(title=title, text=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles类型错误 不是list类型.")

    @staticmethod
    def feed_link(title: str, message_url: str, pic_url: str) -> Any:

        return FeedLink(title=title, message_url=message_url, pic_url=pic_url)

    def send_feed_link(self, *arg) -> None:
        try:
            self.xiaoDing.send_feed_card(list(arg))
        except Exception:
            raise

    def send_ding_notification(self):
        # 发送钉钉通知
        text = f"#### {self.name}自动化通知  \n\n>Python脚本任务: {self.name}\n\n>环境: TEST\n\n>" \
               f"执行人: {self.tester}\n\n>成功率: {self.RATE}% \n\n>总用例数: {self.TOTAL} \n\n>成功用例数: {self.PASS}" \
               f" \n\n>失败用例数: {self.FAILED} \n\n>异常用例数: {self.BROKEN} \n\n>跳过用例数: {self.BROKEN}" \
               f" ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n" \
               f" > ###### 测试报告 [详情](http://{get_host_ip()}:9999/index.html) \n"
        DingTalkSendMsg().send_markdown(
            title="【婚奢汇自动化通知】",
            msg=text,
            mobiles=[18867507063]
        )


if __name__ == '__main__':
    d = DingTalkSendMsg()
    print(d.send_ding_notification())
