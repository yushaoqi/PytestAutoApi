#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 13:32
# @Author : 余少琪

from enum import Enum


class AllureAttachmentType(Enum):
    """
    allure 报告的文件类型枚举
    """
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"

    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"

    PDF = "pdf"

    @staticmethod
    def attachment_types():
        return list(map(lambda c: c.value, AllureAttachmentType))

