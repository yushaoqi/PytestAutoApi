#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:28
# @Author : 余少琪

import os
from typing import Any
from config.setting import ConfigHandler


class Cache:
    """ 设置、读取缓存 """
    def __init__(self, filename: str) -> None:
        self.path = ConfigHandler().cache_path + filename

    def set_cache(self, key, value):
        """
        设置缓存, 只支持设置单字典类型缓存数据, 缓存文件如以存在,则替换之前的缓存内容
        :return:
        """
        with open(self.path, 'w') as f:
            f.write(str({key: value}))

    def set_caches(self, value: any) -> None:
        """
        设置多组缓存数据
        :param value: 缓存内容
        :return:
        """
        with open(self.path, 'w') as f:
            f.write(str(value))

    def get_cache(self) -> Any:
        """
        获取缓存数据
        :return:
        """
        with open(self.path, 'r') as f:
            return f.read()

    def clean_cache(self) -> None:
        if not os.path.exists(self.path):
            raise "您要删除的缓存文件不存在. {0}".format(self.path)
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls) -> None:
        """
        清除所有缓存文件
        :return:
        """
        cache_path = ConfigHandler().cache_path
        # 列出目录下所有文件，生成一个list
        list_dir = os.listdir(cache_path)
        for i in list_dir:
            # 循环删除文件夹下得所有内容
            os.remove(cache_path + i)


if __name__ == '__main__':
    Cache('cache').set_cache('test', 333)