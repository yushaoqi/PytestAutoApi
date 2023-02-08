#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/8 21:37
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : error_case_excel
# @describe:
"""

import json
import shutil
import ast
import xlwings
from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.notify.wechat_send import WeChatSend
from utils.other_tools.allure_data.allure_report_data import AllureFileClean


# TODO 还需要处理动态值
class ErrorTestCase:
    """ 收集错误的excel """
    def __init__(self):
        self.test_case_path = ensure_path_sep("\\report\\html\\data\\test-cases\\")

    def get_error_case_data(self):
        """
        收集所有失败用例的数据
        @return:
        """
        path = get_all_files(self.test_case_path)
        files = []
        for i in path:
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                # 收集执行失败的用例数据
                if date['status'] == 'failed' or date['status'] == 'broken':
                    files.append(date)
        print(files)
        return files

    @classmethod
    def get_case_name(cls, test_case):
        """
        收集测试用例名称
        @return:
        """
        name = test_case['name'].split('[')
        case_name = name[1][:-1]
        return case_name

    @classmethod
    def get_parameters(cls, test_case):
        """
        获取allure报告中的 parameters 参数内容, 请求前的数据
        用于兼容用例执行异常，未发送请求导致的情况
        @return:
        """
        parameters = test_case['parameters'][0]['value']
        return ast.literal_eval(parameters)

    @classmethod
    def get_test_stage(cls, test_case):
        """
        获取allure报告中请求后的数据
        @return:
        """
        test_stage = test_case['testStage']['steps']
        return test_stage

    def get_case_url(self, test_case):
        """
        获取测试用例的 url
        @param test_case:
        @return:
        """
        # 判断用例步骤中的数据是否异常
        if test_case['testStage']['status'] == 'broken':
            # 如果异常状态下，则获取请求前的数据
            _url = self.get_parameters(test_case)['url']
        else:
            # 否则拿请求步骤的数据，因为如果设计到依赖，会获取多组，因此我们只取最后一组数据内容
            _url = self.get_test_stage(test_case)[-7]['name'][7:]
        return _url

    def get_method(self, test_case):
        """
        获取用例中的请求方式
        @param test_case:
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _method = self.get_parameters(test_case)['method']
        else:
            _method = self.get_test_stage(test_case)[-6]['name'][6:]
        return _method

    def get_headers(self, test_case):
        """
        获取用例中的请求头
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _headers = self.get_parameters(test_case)['headers']
        else:
            # 如果用例请求成功，则从allure附件中获取请求头部信息
            _headers_attachment = self.get_test_stage(test_case)[-5]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _headers_attachment)
            with open(path, 'r', encoding='utf-8') as file:
                _headers = json.load(file)
        return _headers

    def get_request_type(self, test_case):
        """
        获取用例的请求类型
        @param test_case:
        @return:
        """
        request_type = self.get_parameters(test_case)['requestType']
        return request_type

    def get_case_data(self, test_case):
        """
        获取用例内容
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _case_data = self.get_parameters(test_case)['data']
        else:
            _case_data_attachments = self.get_test_stage(test_case)[-4]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _case_data_attachments)
            with open(path, 'r', encoding='utf-8') as file:
                _case_data = json.load(file)
        return _case_data

    def get_dependence_case(self, test_case):
        """
        获取依赖用例
        @param test_case:
        @return:
        """
        _dependence_case_data = self.get_parameters(test_case)['dependence_case_data']
        return _dependence_case_data

    def get_sql(self, test_case):
        """
        获取 sql 数据
        @param test_case:
        @return:
        """
        sql = self.get_parameters(test_case)['sql']
        return sql

    def get_assert(self, test_case):
        """
        获取断言数据
        @param test_case:
        @return:
        """
        assert_data = self.get_parameters(test_case)['assert_data']
        return assert_data

    @classmethod
    def get_response(cls, test_case):
        """
        获取响应内容的数据
        @param test_case:
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _res_date = test_case['testStage']['statusMessage']
        else:
            try:
                res_data_attachments = \
                    test_case['testStage']['steps'][-1]['attachments'][0]['source']
                path = ensure_path_sep("\\report\\html\\data\\attachments\\" + res_data_attachments)
                with open(path, 'r', encoding='utf-8') as file:
                    _res_date = json.load(file)
            except FileNotFoundError:
                # 程序中没有提取到响应数据，返回None
                _res_date = None
        return _res_date

    @classmethod
    def get_case_time(cls, test_case):
        """
        获取用例运行时长
        @param test_case:
        @return:
        """

        case_time = str(test_case['time']['duration']) + "ms"
        return case_time

    @classmethod
    def get_uid(cls, test_case):
        """
        获取 allure 报告中的 uid
        @param test_case:
        @return:
        """
        uid = test_case['uid']
        return uid


class ErrorCaseExcel:
    """ 收集运行失败的用例，整理成excel报告 """
    def __init__(self):
        _excel_template = ensure_path_sep("\\utils\\other_tools\\allure_data\\自动化异常测试用例.xlsx")
        self._file_path = ensure_path_sep("\\Files\\" + "自动化异常测试用例.xlsx")
        # if os.path.exists(self._file_path):
        #     os.remove(self._file_path)

        shutil.copyfile(src=_excel_template, dst=self._file_path)
        # 打开程序（只打开不新建)
        self.app = xlwings.App(visible=False, add_book=False)
        self.w_book = self.app.books.open(self._file_path, read_only=False)

        # 选取工作表：
        self.sheet = self.w_book.sheets['异常用例']  # 或通过索引选取
        self.case_data = ErrorTestCase()

    def background_color(self, position: str, rgb: tuple):
        """
        excel 单元格设置背景色
        @param rgb: rgb 颜色 rgb=(0，255，0)
        @param position: 位置，如 A1, B1...
        @return:
        """
        # 定位到单元格位置
        rng = self.sheet.range(position)
        excel_rgb = rng.color = rgb
        return excel_rgb

    def column_width(self, position: str, width: int):
        """
        设置列宽
        @return:
        """
        rng = self.sheet.range(position)
        # 列宽
        excel_column_width = rng.column_width = width
        return excel_column_width

    def row_height(self, position, height):
        """
        设置行高
        @param position:
        @param height:
        @return:
        """
        rng = self.sheet.range(position)
        excel_row_height = rng.row_height = height
        return excel_row_height

    def column_width_adaptation(self, position):
        """
        excel 所有列宽度自适应
        @return:
        """
        rng = self.sheet.range(position)
        auto_fit = rng.columns.autofit()
        return auto_fit

    def row_width_adaptation(self, position):
        """
        excel 设置所有行宽自适应
        @return:
        """
        rng = self.sheet.range(position)
        row_adaptation = rng.rows.autofit()
        return row_adaptation

    def write_excel_content(self, position: str, value: str):
        """
        excel 中写入内容
        @param value:
        @param position:
        @return:
        """
        self.sheet.range(position).value = value

    def write_case(self):
        """
        用例中写入失败用例数据
        @return:
        """

        _data = self.case_data.get_error_case_data()
        # 判断有数据才进行写入
        if len(_data) > 0:
            num = 2
            for data in _data:
                self.write_excel_content(position="A" + str(num), value=str(self.case_data.get_uid(data)))
                self.write_excel_content(position='B' + str(num), value=str(self.case_data.get_case_name(data)))
                self.write_excel_content(position="C" + str(num), value=str(self.case_data.get_case_url(data)))
                self.write_excel_content(position="D" + str(num), value=str(self.case_data.get_method(data)))
                self.write_excel_content(position="E" + str(num), value=str(self.case_data.get_request_type(data)))
                self.write_excel_content(position="F" + str(num), value=str(self.case_data.get_headers(data)))
                self.write_excel_content(position="G" + str(num), value=str(self.case_data.get_case_data(data)))
                self.write_excel_content(position="H" + str(num), value=str(self.case_data.get_dependence_case(data)))
                self.write_excel_content(position="I" + str(num), value=str(self.case_data.get_assert(data)))
                self.write_excel_content(position="J" + str(num), value=str(self.case_data.get_sql(data)))
                self.write_excel_content(position="K" + str(num), value=str(self.case_data.get_case_time(data)))
                self.write_excel_content(position="L" + str(num), value=str(self.case_data.get_response(data)))
                num += 1
            self.w_book.save()
            self.w_book.close()
            self.app.quit()
            # 有数据才发送企业微信
            WeChatSend(AllureFileClean().get_case_count()).send_file_msg(self._file_path)


if __name__ == '__main__':
    ErrorCaseExcel().write_case()
