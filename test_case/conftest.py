#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/28 23:05
# @Author : 余少琪
import pytest
import os
from config.setting import ConfigHandler
from tools.logControl import ERROR, INFO
from tools.gettimeControl import NowTime
from tools.weChatSendControl import WeChatSend
from tools.dingtalkControl import DingTalkSendMsg
from tools.localIpControl import get_host_ip
from tools.yamlControl import GetYamlData

_PROJECT_NAME = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]


@pytest.fixture(scope="session", autouse=True)
def clear_report():
    try:
        for one in os.listdir(ConfigHandler.report_path + f'/tmp'):
            if 'json' in one:
                os.remove(ConfigHandler.report_path + f'/tmp/{one}')
            if 'txt' in one:
                os.remove(ConfigHandler.report_path + f'/tmp/{one}')
    except Exception as e:
        print("allure数据清除失败", e)

    yield


def sendDingNotification(totalNum: int, passNum: int, failNum: int,
                         errorNum: int, skipNum: int, passRate):
    # 发送钉钉通知
    text = f"#### 婚奢汇自动化通知  \n\n>Python脚本任务: {_PROJECT_NAME}\n\n>环境: TEST\n\n>" \
           f"执行人: 余少琪\n\n>执行结果: {passRate} \n\n>总用例数: {totalNum} \n\n>成功用例数: {passNum}" \
           f" \n\n>失败用例数: {failNum} \n\n>异常用例数: {errorNum} \n\n>跳过用例数: {skipNum}" \
           f" ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n" \
           f" > ###### 测试报告 [详情](http://{get_host_ip()}:9999/index.html) \n"
    DingTalkSendMsg().send_markdown(
        title="【婚奢汇自动化通知】",
        msg=text
        , mobiles=[18867507063]
    )


def sendEmailNotification(passNum: int, failNum: int,
                          errorNum: int, skipNum: int, passRate):
    # 发送企业微信通知
    text = """【{0}自动化通知】
                                >测试环境：<font color=\"info\">TEST</font>
                                >测试负责人：@余少琪
                                >
                                > **执行结果**
                                ><font color=\"info\">{1}</font>
                                >成功用例数：<font color=\"info\">{2}</font>
                                >失败用例数：`{3}个`
                                >异常用例数：`{4}个`
                                >跳过用例数：<font color=\"warning\">{5}个</font>
                                >时　间：<font color=\"comment\">{6}</font>
                                >
                                >非相关负责人员可忽略此消息。
                                >测试报告，点击查看>>[测试报告入口](http://121.43.35.47/:9999/index.html)""" \
        .format(_PROJECT_NAME, passRate, passNum, failNum, errorNum, skipNum, NowTime())

    WeChatSend().sendMarkdownMsg(text)


def getNotificationType():
    # 获取报告通知类型，是发送钉钉还是企业邮箱
    Date = GetYamlData(ConfigHandler.config_path).get_yaml_data()['NotificationType']
    return Date


def pytest_terminal_summary(terminalreporter):
    """
    收集用例结果
    :param terminalreporter: 内部使用的终端测试报告对象
    :return:
    """
    try:
        totalNum = terminalreporter._numcollected
        passNum = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
        failNum = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
        errorNum = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
        skipNum = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
        passRate = '成功率：%.2f' % (
                len(terminalreporter.stats.get('passed', [])) / terminalreporter._numcollected * 100) + '%'

        # INFO.logger.info(terminalreporter.stats)
        INFO.logger.info("执行用例总数: {}".format(totalNum))
        INFO.logger.info(
            "执行通过用例数:{}".format(passNum))
        ERROR.logger.error(
            "执行失败用例数:{}".format(failNum))
        INFO.logger.info(
            "执行异常用例数:{}".format(errorNum))
        INFO.logger.info(
            "执行跳过用例数:{}".format(skipNum))
        INFO.logger.info(
            '执行成功率: {}'.format(passRate))

        # TODO 完善失败用例负责人，用例执行失败@对应的负责人
        if getNotificationType() == 1:
            # 发送钉钉通知
            sendDingNotification(totalNum, passNum, failNum, errorNum, skipNum, passRate)
        elif getNotificationType() == 2:
            # 发送企业微信通知
            sendEmailNotification(passNum, failNum, errorNum, skipNum, passRate)
        else:
            raise "NotificationType配置不正确，现在只支持企业微信通知和邮箱通知"

    except ZeroDivisionError:
        raise "程序中未发现可执行测试用例，请检查是否创建测试用例或者用例是否以test开头"
