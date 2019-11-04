#!/usr/bin/python
# coding:utf-8

from .connect import Connect


class ReportsDao(Connect):
    """研报同步数据，错误记录库"""
    collect = 'reports'

    def __init__(self, db='mongodb'):
        Connect.__init__(self, db)

    def get_collects(self):
        """
        获取集合
        :return:
        """
        return self.collect


