#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/19 12:35
# @Author : 余少琪
import json

import xlrd
from xlutils.copy import copy
from config.setting import ConfigHandler


def get_excelData(sheetName: str, caseName: any) -> list:
    """
    读取 Excel 中的数据
    :param sheetName: excel 中的 sheet 页的名称
    :param caseName: 测试用例名称
    :return:
    """
    resList = []

    excelDire = ConfigHandler.excel_path + 'Login.xls'
    workBook = xlrd.open_workbook(excelDire, formatting_info=True)

    # 打开对应的子表
    workSheet = workBook.sheet_by_name(sheetName)
    # 读取一行
    idx = 0
    for one in workSheet.col_values(0):
        # 运行需要运行的测试用例
        if caseName in one:
            reqBodyData = workSheet.cell(idx, 9).value
            respData = workSheet.cell(idx, 11).value
            resList.append((reqBodyData, json.loads(respData)))
        idx += 1
    print(resList)
    return resList


def set_excelData(sheetIndex: int) -> tuple:
    """
    excel 写入
    :return:
    """
    excelDire = r'..\data\Login.xls'
    workBook = xlrd.open_workbook(excelDire, formatting_info=True)
    workBookNew = copy(workBook)

    workSheetNew = workBookNew.get_sheet(sheetIndex)
    return workBookNew, workSheetNew


if __name__ == '__main__':
    get_excelData("登录", 'Login001')

