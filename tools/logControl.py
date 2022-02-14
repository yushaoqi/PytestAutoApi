#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 13:05
# @Author : 余少琪

import logging
from logging import handlers
import colorlog
from config.setting import ConfigHandler


class LogHandler(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3, fmt='%%(levelname)-8s%(asctime)s '
                                                                          '%(name)s:%(filename)s:%(lineno)d %(message)s'):
        self.logger = logging.getLogger(filename)

        self.log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=self.log_colors_config)

        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 往屏幕上输出
        sh = logging.StreamHandler()
        # 设置屏幕上显示的格式
        sh.setFormatter(formatter)
        # 往文件里写入#指定间隔时间自动生成文件的处理器
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        """
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨    
        """
        # 设置文件里写入的格式
        th.setFormatter(format_str)
        # 把对象加到logger里
        self.logger.addHandler(sh)
        self.logger.addHandler(th)
        self.log_path = ConfigHandler.log_path


INFO = LogHandler(ConfigHandler.info_log_path, level='info')
ERROR = LogHandler(ConfigHandler.error_log_path, level='error')
WARNING = LogHandler(ConfigHandler.warning_log_path, level='warning')

if __name__ == '__main__':
    INFO.logger.info("测试")

    # msg = '111'
    # log = LogHandler(level='debug')
    # log.logger.debug('debug')
    # log.logger.info(msg)
    # log.logger.warning('警告')
    # log.logger.error('报错')
    # log.logger.critical('严重')
    # LogHandler('error.log', level='error').logger.error('error')
    # # is_open = ReadIni(node='log').get_value("run")
    # INFO.logger.info("111")
