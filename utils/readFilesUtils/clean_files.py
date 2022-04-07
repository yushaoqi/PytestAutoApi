#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/4/7 11:56
# @Author : 余少琪

import os


def del_file(path):
    """删除目录下的文件"""
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
