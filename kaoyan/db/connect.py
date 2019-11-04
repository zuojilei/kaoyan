#!/usr/bin/python
# coding:utf-8
import redis
import pymongo
import pymssql
from kaoyan.tool.config import ConfigTool
from abc import ABCMeta, abstractmethod


class Connect(object):
    """连接mongodb数据库"""
    __metaclass__ = ABCMeta
    collects = ''

    def __init__(self, db='mongodb'):
        self.client = pymongo.MongoClient(ConfigTool().get(db, 'host'))
        self.conn = self.client[ConfigTool().get(db, 'db')]

    def insert_one(self, param):
        """
        插入一个文档
        :param param:  文档
        :return:
        """
        cur = self.conn[self.get_collects()]
        return cur.insert_one(param)

    def insert_many(self, param):
        """
        插入多个文档
        :param param:
        :return:
        """
        cur = self.conn[self.get_collects()]
        return cur.insert_many(param)

    def find(self, where={}, skip=0, limit_num=10):
        """
        查询数据
        :param where: 条件
        :param fields: 查询数据
        :param pageSize: 多少数据
        :param skip:
        :param limit_num:
        :return:
        """
        cur = self.conn[self.get_collects()]
        return cur.find(where).skip(skip)

    def find_one(self, where, param={}):
        """
        查询一条记录
        :param where:
        :param param:
        :return:
        """
        cur = self.conn[self.get_collects()]

        return cur.find_one(where, param)

    def is_exist_sid(self, sid):
        """
        清洗库是否存在
        :param sid:
        :return:
        """

        cur = self.conn[self.get_collects()]
        return not cur.find_one({"sid": sid}, {"sid": 1})

    def is_exist_id(self, id):
        """
        清洗库是否存在(文书)
        :param sid:
        :return:
        """

        cur = self.conn[self.get_collects()]
        return not cur.find_one({"id": id}, {"id": 1})

    def get_cur(self):
        """
        获取cur 游标
        :return:
        """
        return self.conn[self.get_collects()]

    def delete_one(self, where):
        """
        删除一个元素
        :param where:
        :return:
        """
        cur = self.conn[self.get_collects()]
        return cur.delete_one(where)

    def update_one(self, where, param):
        """
        修改一条记录
        :param where:
        :param param:
        :return:
        """
        cur = self.conn[self.get_collects()]
        return cur.update_one(where, {"$set": param})

    def close(self):
        """关闭连接"""
        self.client.close()

    @abstractmethod
    def get_collects(self):
        pass

    def set_db(self, dbName):
        """
        设置数据库
        """
        self.conn = self.client[dbName]

    def set_collects(self, collect):
        """
        设置集合名
        :param collect:
        :return:
        """
        self.collect = collect


class MSSQL(object):
    """sqlserver的连接"""

    def __init__(self):
        self.host = ConfigTool().get('mssql', 'mssql_host')
        self.port =  ConfigTool().get('mssql', 'mssql_port')
        self.user = ConfigTool().get('mssql', 'mssql_user')
        self.pwd = ConfigTool().get('mssql', 'mssql_pwd')
        self.db = ConfigTool().get('mssql', 'mssql_db')
        self.table = 'bigdata'

    def GetConnect(self):
        """
         得到连接信息
        返回: conn.cursor()
        :return: cur 游标
        """
        if not self.db:
            raise(NameError,"没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host,port=self.port,user=self.user,password=self.pwd,database=self.db,
                                    charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecNonQuery(self,sql):
        """
        执行非查询语句
        :param sql:
        :return:
        """
        cur = self.GetConnect()
        aeq = cur.execute(sql)
        self.conn.commit()
        return aeq

    @abstractmethod
    def get_table(self):
        pass

    def close(self):
        self.conn.close()

    def set_table(self,table):
        self.table = table

    def create_table(self):
        cur = self.GetConnect()
        sql =  "create table "+self.table + " (" \
               "id int IDENTITY (1,1) PRIMARY KEY," \
               "title VARCHAR(256) NOT NULL," \
               "img TEXT NULL DEFAULT ''," \
               "sid VARCHAR(64) NOT NULL," \
               "pdate VARCHAR(50) NOT NULL DEFAULT ''," \
               "industry VARCHAR(128) NULL DEFAULT ''," \
               "src VARCHAR(256) NOT NULL," \
               "enact VARCHAR(100) NOT NULL," \
               "digest TEXT NULL DEFAULT ''," \
               "content TEXT NULL DEFAULT ''," \
               "author VARCHAR (64) NULL DEFAULT ''," \
               "download_status VARCHAR(10) NOT NULL," \
               "page VARCHAR(50) NOT NULL DEFAULT ''," \
               "pdf_url VARCHAR(256) NOT NULL DEFAULT ''," \
               "read_num VARCHAR(10) NOT NULL DEFAULT ''," \
               "download_num VARCHAR(10) NOT NULL DEFAULT ''," \
               "source VARCHAR(50) NOT NULL DEFAULT '')"
        cur.execute(sql)
        self.conn.commit()


if __name__ == '__main__':
    MSSQL().create_table()


class RedisDao(object):
    """连接redis"""

    def __init__(self, config='redis', db=0):
        self.conn = redis.Redis(
            host=ConfigTool().get(config, 'host'),
            port=int(ConfigTool().get(config, 'port')),
            password=ConfigTool().get(config, 'password'),
            decode_responses=True,
            db=db
        )

    def close(self):
        """
        关闭redis连接
        :return:
        """
        self.close()

    def get_set(self, name):
        return self.conn.smembers(name)

    #
    def get_name(self, name):
        """
        获取值 获取key对应的value
        :param name:
        :return:
        """
        return self.conn.get(name)

    def set_name(self, name, value, ex=None):
        """
        设置value值
        :param name:
        :param value:
        :param ex:
        :return:
        """
        return self.conn.set(name, value, ex)

    def spop(self, name):
        """
        从集合右侧中移除一个元素
        :param name:
        :return:
        """
        return self.conn.spop(name)

    def sadd(self, name, item):
        """
        向集合中添加一个元素
        :param name:
        :param item:
        :return:
        """
        return self.conn.sadd(name, item)






