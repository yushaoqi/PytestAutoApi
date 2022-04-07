#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/4/7 17:53
# @Author : 余少琪

import allure
import json
from Enums.allureAttchementType_enum import AllureAttachmentType


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
    _NAME = name.split('.')[-1]
    attachment_type = None
    if _NAME == AllureAttachmentType.TEXT.value:
        attachment_type = allure.attachment_type.TEXT
    elif _NAME == AllureAttachmentType.CSV.value:
        attachment_type = allure.attachment_type.CSV
    elif _NAME == AllureAttachmentType.TSV.value:
        attachment_type = allure.attachment_type.TSV
    elif _NAME == AllureAttachmentType.URI_LIST.value:
        attachment_type = allure.attachment_type.URI_LIST
    elif _NAME == AllureAttachmentType.HTML.value:
        attachment_type = allure.attachment_type.HTML
    elif _NAME == AllureAttachmentType.XML.value:
        attachment_type = allure.attachment_type.XML
    elif _NAME == AllureAttachmentType.PCAP.value:
        attachment_type = allure.attachment_type.PCAP
    elif _NAME == AllureAttachmentType.PNG.value:
        attachment_type = allure.attachment_type.PNG
    elif _NAME == AllureAttachmentType.JPG.value:
        attachment_type = allure.attachment_type.JPG
    elif _NAME == AllureAttachmentType.SVG.value:
        attachment_type = allure.attachment_type.SVG
    elif _NAME == AllureAttachmentType.GIF.value:
        attachment_type = allure.attachment_type.GIF
    elif _NAME == AllureAttachmentType.BMP.value:
        attachment_type = allure.attachment_type.BMP
    elif _NAME == AllureAttachmentType.TIFF.value:
        attachment_type = allure.attachment_type.TIFF
    elif _NAME == AllureAttachmentType.MP4.value:
        attachment_type = allure.attachment_type.MP4
    elif _NAME == AllureAttachmentType.OGG.value:
        attachment_type = allure.attachment_type.OGG
    elif _NAME == AllureAttachmentType.WEBM.value:
        attachment_type = allure.attachment_type.WEBM
    elif _NAME == AllureAttachmentType.SVG.PDF:
        attachment_type = allure.attachment_type.PDF
    # else:
    #     raise ValueError(f"allure暂不支持该文件类型, 文件路径: {source}")
    allure.attach.file(source=source, name=name, attachment_type=attachment_type, extension=extension)


def allure_step_no(step: str):
    """
    无附件的操作步骤
    :param step: 步骤名称
    :return:
    """
    with allure.step(step):
        pass
