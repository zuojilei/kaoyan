#!/bin/python
# coding:utf8

import configparser
import threading


class ConfigTool(object):
    """
    配置文件管理类
    """

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        单例模块
        :param args:
        :param kwargs:
        :return:
        """
        if not hasattr(ConfigTool, "_instance"):
            cls.config = configparser.ConfigParser()
            cls.config.read('C:\\workspace\\kaoyan\\kaoyan\\conf\\env.ini', encoding='utf8')
            with ConfigTool._instance_lock:
                if not hasattr(ConfigTool, "_instance"):
                    ConfigTool._instance = object.__new__(cls, *args, **kwargs)
        return ConfigTool._instance

    def get(self, section, option):
        """
        获取配置文件
        :param section:
        :param option:
        :return:
        """
        return self.config.get(section, option)

    def items(self, section):
        """
        读取section下所有配置
        :param section:
        :return:
        """
        return self.config.items(section)
