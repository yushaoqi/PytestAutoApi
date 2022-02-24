#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 16:20
# @Author : 余少琪


import smtplib
from email.mime.text import MIMEText
from tools.yamlControl import GetYamlData
from config.setting import ConfigHandler
from tools.allureDataControl import CaseCount, AllureFileClean


class SendEmail(object):
    def __init__(self):
        self.getData = GetYamlData(ConfigHandler.config_path).get_yaml_data()['email']
        self.send_user = self.getData['send_user']  # 发件人
        self.email_host = self.getData['email_host']  # QQ 邮件 STAMP 服务器地址
        self.key = self.getData['stmp_key']  # STAMP 授权码
        self.name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]
        self.allureData = CaseCount()
        self.PASS = self.allureData.passCount()
        self.FAILED = self.allureData.failedCount()
        self.BROKEN = self.allureData.brokenCount()
        self.SKIP = self.allureData.skippedCount()
        self.TOTAL = self.allureData.totalCount()
        self.RATE = self.allureData.passRate()
        self.CaseDetail = AllureFileClean().getFailedCasesDetail()

    def send_mail(self, user_list: list, sub, content):
        """

        @param user_list: 发件人邮箱
        @param sub:
        @param content: 发送内容
        @return:
        """
        user = "yushaoqi" + "<" + self.send_user + ">"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')
        message['Subject'] = sub
        message['From'] = user
        message['To'] = ";".join(user_list)
        server = smtplib.SMTP()
        server.connect(self.email_host)
        server.login(self.send_user, self.key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message):
        """
        执行异常邮件通知
        @param error_message: 报错信息
        @return:
        """
        emali = self.getData['send_list']
        user_list = emali.split(',')  # 多个邮箱发送，config文件中直接添加  '806029174@qq.com'

        sub = self.name + "接口自动化执行异常通知"
        content = "自动化测试执行完毕，程序中发现异常，请悉知。报错信息如下：\n{0}".format(error_message)
        self.send_mail(user_list, sub, content)

    def send_main(self):
        """
        发送邮件
        :return:
        """

        emali = self.getData["send_list"]
        user_list = emali.split(',')  # 多个邮箱发送，yaml文件中直接添加  '806029174@qq.com'

        sub = self.name + "接口自动化报告"
        content = """
        各位同事, 大家好:
            自动化用例执行完成，执行结果如下:
            用例运行总数: {} 个
            通过用例个数: {} 个
            失败用例个数: {} 个
            异常用例个数: {} 个
            跳过用例个数: {} 个
            成  功   率: {} %
            
        {}

        **********************************
        jenkins地址：https://121.xx.xx.47:8989/login
        详细情况可登录jenkins平台查看，非相关负责人员可忽略此消息。谢谢。
        """.format(self.TOTAL, self.PASS, self.FAILED, self.BROKEN, self.SKIP, self.RATE, self.CaseDetail)

        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail().send_main()
