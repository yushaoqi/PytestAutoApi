#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 14:17
# @Author : 余少琪

from config.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData


TestData = CaseData(ConfigHandler.data_path + r'WorkApplyCenter/sup_apply_list.yaml').case_process()

is_run = [i for i in TestData if i['is_run'] is False]

print(is_run)