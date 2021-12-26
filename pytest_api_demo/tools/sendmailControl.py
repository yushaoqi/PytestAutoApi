#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 16:20
# @Author : 余少琪


import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tools.yamlControl import GetYamlData
from config.setting import ConfigHandler


class SendEmail(object):
    def __init__(self):
        self.getData = GetYamlData(ConfigHandler.config_path).get_yaml_data()['email']
        self.send_user = self.getData['send_user']  # 发件人
        self.email_host = self.getData['email_host']  # QQ 邮件 STAMP 服务器地址
        self.key = self.getData['stmp_key']  # STAMP 授权码
        self.name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]

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

    def send_main(self, pass_list, fail_list, time):
        """
        发送测试报告
        @param pass_list: 通过用例数
        @param fail_list: 失败用例数
        @param time: 执行时间
        @return:
        """
        pass_num = len(pass_list)
        fail_num = len(fail_list)
        count_num = pass_num + fail_num
        pass_result = '%.2f%%' % (pass_num / count_num * 100)
        fail_result = '%.2f%%' % (fail_num / count_num * 100)

        emali = self.getData["send_list"]
        user_list = emali.split(',')  # 多个邮箱发送，yaml文件中直接添加  '806029174@qq.com'

        sub = self.name + "接口自动化报告"
        content = "此次一共运行接口个数为{0}个, 通过个数为{1}个, 失败个数为{2}个， 通过率为{3}, 失败率为{4}，共耗时{5}。".format(
            count_num, pass_num, fail_num, pass_result, fail_result, time)

        msg = MIMEMultipart()
        # 发送附件
        part = MIMEApplication(open(self.getData, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename="自动化测试报告.xlsx")
        msg.attach(part)
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    MIME-Version: 1.0
    Content-type: text/html
    Subject: SMTP HTML e-mail test.yaml

    This is an e-mail message to be sent in HTML format

    <b>This is HTML message.</b>
    <h1>This is headline.</h1>
    """
    SendEmail().send_main([1, 2, 3], [], 3)
    SendEmail().error_mail("NameError")
