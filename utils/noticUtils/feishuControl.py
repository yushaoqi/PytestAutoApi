from json import JSONDecodeError
import requests
import json
import logging
import time
import urllib3
import datetime

from config.setting import ConfigHandler
from utils.readFilesUtils.yamlControl import GetYamlData
from utils.otherUtils.allureDate.allure_report_data import CaseCount

urllib3.disable_warnings()

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
  非空字符串
  :param content: 字符串
  :return: 非空 - True，空 - False
  """
    if content and content.strip():
        return True
    else:
        return False


class FeiShuTalkChatBot(object):
    """飞书机器人通知"""
    def __init__(self):

        self.timeStamp = str(round(time.time() * 1000))
        self.devConfig = ConfigHandler()
        # 从yaml文件中获取钉钉配置信息

        self.name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]
        self.test_name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TesterName']
        self.host = GetYamlData(ConfigHandler.config_path).get_yaml_data()['Env']
        self.tester = GetYamlData(ConfigHandler.config_path).get_yaml_data()
        self.allure_data = CaseCount()
        self.PASS = self.allure_data.pass_count()
        self.FAILED = self.allure_data.failed_count()
        self.BROKEN = self.allure_data.broken_count()
        self.SKIP = self.allure_data.skipped_count()
        self.TOTAL = self.allure_data.total_count()
        self.RATE = self.allure_data.pass_rate()

        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.devConfig = ConfigHandler()
        self.getFeiShuTalk = GetYamlData(self.devConfig.config_path).get_yaml_data()['FeiShuTalk']
        self.webhook = self.getFeiShuTalk["webhook"]

    def send_text(self, msg: str):
        """
    消息类型为text类型
    :param msg: 消息内容
    :return: 返回消息发送结果
    """
        data = {"msg_type": "text", "at": {}}
        if is_not_null_and_blank_str(msg):  # 传入msg非空
            data["content"] = {"text": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        logging.debug('text类型：%s' % data)
        return self.post()

    def post(self):
        """
    发送消息（内容UTF-8编码）
    :return: 返回消息发送结果
    """
        rich_text = {
            "email": "fanlv@bytedance.com",
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "【自动化测试通知】",
                        "content": [
                            [
                                {
                                    "tag": "a",
                                    "text": "测试报告",
                                    "href": "http://192.168.0.72:8080/job/helper_test_adverte/allure/#"
                                },
                                {
                                    "tag": "at",
                                    "user_id": "ou_18eac85d35a26f989317ad4f02e8bbbb"
                                    # "text":"陈锐男"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "测试  人员 : "
                                },
                                {
                                    "tag": "text",
                                    "text": "{testname}".format(testname=self.test_name)
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "运行  环境 : "
                                },
                                {
                                    "tag": "text",
                                    "text": "{host}".format(host=str(self.host))
                                }
                            ],
                            [{
                                "tag": "text",
                                "text": "成   功   率 : "
                            },
                                {
                                    "tag": "text",
                                    "text": "{rate}".format(rate=self.RATE) + " %"
                                }],  # 成功率

                            [{
                                "tag": "text",
                                "text": "成功用例数 : "
                            },
                                {
                                    "tag": "text",
                                    "text": "{total}".format(total=self.PASS)
                                }],  # 成功用例数

                            [{
                                "tag": "text",
                                "text": "失败用例数 : "
                            },
                                {
                                    "tag": "text",
                                    "text": "{failed}".format(failed=self.FAILED)
                                }],  # 失败用例数
                            [{
                                "tag": "text",
                                "text": "异常用例数 : "
                            },
                                {
                                    "tag": "text",
                                    "text": "{failed}".format(failed=self.BROKEN)
                                }],  # 损坏用例数
                            [
                                {
                                    "tag": "text",
                                    "text": "时  间 : "
                                },
                                {
                                    "tag": "text",
                                    "text": "{test}".format(test=datetime.datetime.now().strftime('%Y-%m-%d'))
                                }
                            ],

                            [
                                {
                                    "tag": "img",
                                    "image_key": "d640eeea-4d2f-4cb3-88d8-c964fab53987",
                                    "width": 300,
                                    "height": 300
                                }
                            ]
                        ]
                    }
                }
            }
        }
        try:
            post_data = json.dumps(rich_text)
            response = requests.post(self.webhook, headers=self.headers, data=post_data, verify=False)
        except requests.exceptions.HTTPError as exc:
            logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            logging.error("消息发送失败，HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            logging.error("消息发送失败，Timeout error!")
            raise
        except requests.exceptions.RequestException:
            logging.error("消息发送失败, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '服务器响应异常'}
            else:
                logging.debug('发送结果：%s' % result)
                # 消息发送失败提醒（errcode 不为 0，表示消息发送异常），默认不提醒，开发者可以根据返回的消息发送结果自行判断和处理
                if result.get('StatusCode') != 0:
                    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    error_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "[注意-自动通知]飞书机器人消息发送失败，时间：%s，原因：%s，请及时跟进，谢谢!" % (
                                time_now, result['errmsg'] if result.get('errmsg', False) else '未知异常')
                        },
                        "at": {
                            "isAtAll": False
                        }
                    }
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


if __name__ == '__main__':
    send = FeiShuTalkChatBot()
    send.post()
