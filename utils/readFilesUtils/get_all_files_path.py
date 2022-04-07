#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 13:22
# @Author : 余少琪
import os


def get_all_files(file_path) -> list:
    """ 获取所有 yaml 文件 """
    filename = []
    # 获取所有文件下的子文件名称
    for root, dirs, files in os.walk(file_path):
        for filePath in files:
            path = os.path.join(root, filePath)
            if '.yaml' in path:
                filename.append(path)
    return filename
