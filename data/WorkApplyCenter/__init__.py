#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 14:56
# @Author : 余少琪
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from config.setting import ConfigHandler

TestData = CaseData(ConfigHandler.data_path + r'WorkApplyCenter/sup_apply_list.yaml').case_process()
print(TestData)
# print([i for i in TestData])
is_run = [i['is_run'] for i in TestData]
print(is_run)