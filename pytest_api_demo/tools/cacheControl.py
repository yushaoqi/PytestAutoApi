#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 21:56
# @Author : 余少琪
from setting import ConfigHandler
import os


class Cache:
    """ 设置、读取缓存 """
    def __init__(self, filename: str):
        self.path = ConfigHandler().cache_path + "/" + filename + '.txt'

    def set_cache(self, key, value):
        """
        设置缓存, 只支持设置单字典类型缓存数据, 缓存文件如以存在,则替换之前的缓存内容
        :return:
        """
        with open(self.path, 'w') as f:
            f.write(str({key: value}))

    def set_caches(self, value: dict):
        """
        设置多组缓存数据
        :param value: 缓存内容
        :return:
        """
        if isinstance(value, dict):
            with open(self.path, 'w') as f:
                f.write(str(value))

        else:
            raise "缓存类型必须要是 dict 类型"

    def get_cache(self):
        """
        获取缓存数据
        :return:
        """
        with open(self.path, 'r') as f:
            return f.read()

    def clean_cache(self):
        if not os.path.exists(self.path):
            raise "您要删除的缓存文件不存在. {0}".format(self.path)
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls):
        """
        清除所有缓存文件
        :return:
        """
        cache_path = ConfigHandler().cache_path
        # 列出目录下所有文件，生成一个list
        list_dir = os.listdir(cache_path)
        for i in list_dir:
            # 循环删除文件夹下得所有内容
            os.remove(cache_path + "/" + i)


if __name__ == '__main__':
    Cache('cache').clean_all_cache()
