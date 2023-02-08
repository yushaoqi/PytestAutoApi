#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/4/7 17:53
# @Author : 余少琪
"""
import json
import allure
from utils.other_tools.models import AllureAttachmentType


def allure_step(step: str, var: str) -> None:
    """
    :param step: 步骤及附件名称
    :param var: 附件内容
    """
    with allure.step(step):
        allure.attach(
            json.dumps(
                str(var),
                ensure_ascii=False,
                indent=4),
            step,
            allure.attachment_type.JSON)


def allure_attach(source: str, name: str, extension: str):
    """
    allure报告上传附件、图片、excel等
    :param source: 文件路径，相当于传一个文件
    :param name: 附件名称
    :param extension: 附件的拓展名称
    :return:
    """
    # 获取上传附件的尾缀，判断对应的 attachment_type 枚举值
    _name = name.split('.')[-1].upper()
    _attachment_type = getattr(AllureAttachmentType, _name, None)

    allure.attach.file(
        source=source,
        name=name,
        attachment_type=_attachment_type if _attachment_type is None else _attachment_type.value,
        extension=extension
    )


def allure_step_no(step: str):
    """
    无附件的操作步骤
    :param step: 步骤名称
    :return:
    """
    with allure.step(step):
        pass
