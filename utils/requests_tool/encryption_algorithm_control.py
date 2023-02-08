#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/23 21:27
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : encryption_algorithm_control
# @describe:
"""

import hashlib
from hashlib import sha256
import hmac
from typing import Text
import binascii
from pyDes import des, ECB, PAD_PKCS5


def hmac_sha256_encrypt(key, data):
    """hmac sha 256算法"""
    _key = key.encode('utf8')
    _data = data.encode('utf8')
    encrypt_data = hmac.new(_key, _data, digestmod=sha256).hexdigest()
    return encrypt_data


def md5_encryption(value):
    """ md5 加密"""
    str_md5 = hashlib.md5(str(value).encode(encoding='utf-8')).hexdigest()
    return str_md5


def sha1_secret_str(_str: Text):
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    encrypts = hashlib.sha1(_str.encode('utf-8')).hexdigest()
    return encrypts


def des_encrypt(_str):
    """
    DES 加密
    :return: 加密后字符串，16进制
    """
    # 密钥，自行修改
    _key = 'PASSWORD'
    secret_key = _key
    _iv = secret_key
    key = des(secret_key, ECB, _iv, pad=None, padmode=PAD_PKCS5)
    _encrypt = key.encrypt(_str, padmode=PAD_PKCS5)
    return binascii.b2a_hex(_encrypt)


def encryption(ency_type):
    """
    :param ency_type: 加密类型
    :return:
    """

    def decorator(func):
        def swapper(*args, **kwargs):
            res = func(*args, **kwargs)
            _data = res['body']
            if ency_type == "md5":
                def ency_value(data):
                    if data is not None:
                        for key, value in data.items():
                            if isinstance(value, dict):
                                ency_value(data=value)
                            else:
                                data[key] = md5_encryption(value)
            else:
                raise ValueError("暂不支持该加密规则，如有需要，请联系管理员")
            ency_value(_data)
            return res

        return swapper

    return decorator
