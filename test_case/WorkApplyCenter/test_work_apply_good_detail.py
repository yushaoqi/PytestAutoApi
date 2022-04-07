#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-04-07 22:51:22
# @Author : 余少琪


import allure
import pytest
from config.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl


TestData = CaseData(ConfigHandler.data_path + r'WorkApplyCenter/work_apply_good_detail.yaml').case_process()


@allure.epic("电商平台端")
@allure.feature("审核中心")
class TestWorkApplyGoodDetail:

    @allure.story("商品审核详情")
    @pytest.mark.parametrize('in_data', TestData, ids=[i['detail'] for i in TestData])
    def test_work_apply_good_detail(self, in_data, case_skip):
        """
        :param :
        :return:
        """

        res = RequestControl().http_request(in_data)
        Assert(in_data['assert']).assert_equality(response_data=res[0], sql_data=res[1])


if __name__ == '__main__':
    pytest.main(['test_work_apply_good_detail.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
