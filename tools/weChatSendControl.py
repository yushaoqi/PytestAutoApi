#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/10 21:17
# @Author : 余少琪
import json

import requests
from config.setting import ConfigHandler
from tools.yamlControl import GetYamlData


class WeChatSend:
    def __init__(self):
        self.weChatData = GetYamlData(ConfigHandler.config_path).get_yaml_data()['WeChat']
        self.host = self.weChatData['host'] + '/message/send?access_token=' + self.getToken()
        # 获取发送企业微信通知的一些公共数据，全部放在了配置文件中
        self.data = self.weChatData['Data']

    def getToken(self):
        """ 获取企业微信 token """
        _Data = self.weChatData['Token']
        _Host = self.weChatData['host'] + '/gettoken'
        res = requests.get(url=_Host, params=_Data, verify=True)
        if res.json()['errcode'] != 0:
            raise f"企业获取获取access_token失败，失败原因{res.json()}"
        else:
            Token = res.json()['access_token']
        return Token

    def uploadFile(self, fileType, filePath):
        """
        上传临时素材
        :param filePath: 文件路径
        :param fileType: 媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件（file）
        :return:
        """
        try:
            # 判断 fileType 类型
            if fileType == 'image' or fileType == 'voice' or fileType == 'video' or fileType == 'file':
                url = self.weChatData['host'] + f'/media/upload?access_token={self.getToken()}&type={fileType}'
                # 上传文件
                files = [('filename', ('22.jpeg', open(filePath, 'rb'), 'image/jpeg'))]
                headers = {'Content-Type': 'multipart/form-data'}
                res = requests.post(url, headers=headers, files=files)
                if res.json()['errcode'] != 0:
                    raise f"上传文件失败，失败原因{res.json()}"
                else:
                    # 返回文件 ID
                    return res.json()['media_id']
            else:
                raise "fileType 不正确"
        except OSError:
            raise "文件地址不正确"

    def sendTextMsg(self, text):
        """
        发送微信文本消息
        :param text: 消息内容，最长不超过2048个字节，超过将截断（支持id转译）
        :return:
        """

        Data = {"content": text}
        self.data['text'] = Data
        self.data['msgtype'] = 'text'
        res = requests.post(url=self.host, data=json.dumps(self.data))
        if res.json()['errcode'] != 0:
            raise "企业微信「文本消息」消息发送失败，失败原因"

    def sendImageMsg(self, filePath):
        """
        发送图片消息
        :param filePath: 文件路径
        :return:
        """

        Image = {"media_id": self.uploadFile(fileType='image', filePath=filePath)}
        self.data['image'] = Image
        self.data['msgtype'] = 'image'
        res = requests.post(url=self.host, data=json.dumps(self.data))
        if res.json()['errcode'] != 0:
            raise "企业微信「图片消息」消息发送失败"

    def sendTextCardMsg(self, title, description, url, btnText):
        """
        发送文本卡片格式消息
        :param title: 卡片标题
        :param description: 卡片描述
        :param url:
        :param btnText: 按钮文案
        :return:
        """
        textCard = {"title": title, "description": description, "url": url, "btntxt": btnText}
        self.data['textcard'] = textCard
        self.data['msgtype'] = 'textcard'
        res = requests.post(url=self.host, data=json.dumps(self.data))
        if res.json()['errcode'] != 0:
            raise "企业微信「文本卡片类型」消息发送失败"

    def sendMarkdownMsg(self, content):
        pass
        markdown = {"content": content}
        self.data['markdown'] = markdown
        self.data['msgtype'] = 'markdown'
        res = requests.post(url=self.host, data=json.dumps(self.data))
        if res.json()['errcode'] != 0:
            raise "企业微信「文本卡片类型」消息发送失败"


if __name__ == '__main__':
    # 发送markdown
    text = """【婚奢汇自动化通知】
                                >测试环境：<font color=\"info\">TEST</font> 
                                >测试负责人：@余少琪 
                                >
                                > **执行结果**
                                >成  功 率：<font color=\"info\">90%</font> 
                                >成功用例数：<font color=\"info\">54个</font> 
                                >失败用例数：`1个`
                                >异常用例数：`1个` 
                                >跳过用例数：<font color=\"warning\">1个</font> 
                                >时　间：<font color=\"comment\">上午9:00-11:00</font>
                                >
                                >非相关负责人员可忽略此消息。 
                                >测试报告，点击查看>>[测试报告入口](https://work.weixin.qq.com)"""
    WeChatSend().sendMarkdownMsg(text)