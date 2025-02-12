#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
error classes
"""


class BaseError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CopyContentError(BaseError):
    """
    复制失败
    """
    pass


class RightMouseCreateItemNotExist(BaseError):
    """
    右键新建的项目不存在
    """
    pass


class ConfigError(BaseError):
    """
    读取配置文件错误
    """
    pass