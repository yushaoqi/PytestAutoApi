#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 14:59
# @Author : 余少琪


import requests
from config.setting import ConfigHandler
from utils.readFilesUtils.yamlControl import GetYamlData
from utils.logUtils.logControl import ERROR
from utils.otherUtils.allureDate.allure_report_data import CaseCount
from utils.timesUtils.timeControl import NowTime
from utils.otherUtils.localIpControl import get_host_ip
from utils import project_name, tester_name

class WeChatSend:
    """
    企业微信消息通知
    """

    def __init__(self):
        self.weChatData = GetYamlData(ConfigHandler.config_path).get_yaml_data()['WeChat']
        self.curl = self.weChatData['webhook']
        self.headers = {"Content-Type": "application/json"}
        self.allureData = CaseCount()
        self.PASS = self.allureData.pass_count()
        self.FAILED = self.allureData.failed_count()
        self.BROKEN = self.allureData.broken_count()
        self.SKIP = self.allureData.skipped_count()
        self.TOTAL = self.allureData.total_count()
        self.RATE = self.allureData.pass_rate()

    def send_text(self, content, mentioned_mobile_list=None):
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
                        if res.json()['errcode'] != 0:
                            ERROR.logger.error(res.json())
                            raise ValueError(f"企业微信「文本类型」消息发送失败")

                    else:
                        raise TypeError("手机号码必须是字符串类型.")
        else:
            raise ValueError("手机号码列表必须是list类型.")

    def send_markdown(self, content):
        """
        发送 MarkDown 类型消息
        :param content: 消息内容，markdown形式
        :return:
        """
        _DATA = {"msgtype": "markdown", "markdown": {"content": content}}
        res = requests.post(url=self.curl, json=_DATA, headers=self.headers)
        if res.json()['errcode'] != 0:
            ERROR.logger.error(res.json())
            raise ValueError(f"企业微信「MarkDown类型」消息发送失败")

    def articles(self, article):
        """

        发送图文消息
        :param article: 传参示例：{
               "title" : ”标题，不超过128个字节，超过会自动截断“,
               "description" : "描述，不超过512个字节，超过会自动截断",
               "url" : "点击后跳转的链接",
               "picurl" : "图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。"
           }
        如果多组内容，则对象之间逗号隔开传递
        :return:
        """
        _data = {"msgtype": "news", "news": {"articles": [article]}}
        if isinstance(article, dict):
            lists = ['description', "title", "url", "picurl"]
            for i in lists:
                # 判断所有参数都存在
                if article.__contains__(i):
                    res = requests.post(url=self.curl, headers=self.headers, json=_data)
                    if res.json()['errcode'] != 0:
                        ERROR.logger.error(res.json())
                        raise ValueError(f"企业微信「图文类型」消息发送失败")
                else:
                    raise ValueError("发送图文消息失败，标题、描述、链接地址、图片地址均不能为空！")
        else:
            raise TypeError("图文类型的参数必须是字典类型")

    def send_wechat_notification(self):
        # 发送企业微信通知
        text = """【{0}自动化通知】
                                    >测试环境：<font color=\"info\">TEST</font>
                                    >测试负责人：@{1}
                                    >
                                    > **执行结果**
                                    ><font color=\"info\">成功率: {2}%</font>
                                    >成功用例数：<font color=\"info\">{3}</font>
                                    >失败用例数：`{4}个`
                                    >异常用例数：`{5}个`
                                    >跳过用例数：<font color=\"warning\">{6}个</font>
                                    >时　间：<font color=\"comment\">{7}</font>
                                    >
                                    >非相关负责人员可忽略此消息。
                                    >测试报告，点击查看>>[测试报告入口](http://{6}:9999/index.html)""" \
            .format(project_name, tester_name, self.RATE, self.PASS, self.FAILED,
                    self.BROKEN, self.SKIP, NowTime(), get_host_ip())

        WeChatSend().send_markdown(text)


if __name__ == '__main__':
    WeChatSend().send_wechat_notification()