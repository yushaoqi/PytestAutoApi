#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 18:27
# @Author : 余少琪

import pymysql
from warnings import filterwarnings
from tools.yamlControl import GetYamlData
from tools.logControl import ERROR
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler
from tools.regularControl import SqlRegular

# 忽略 Mysql 告警信息
filterwarnings("ignore", category=pymysql.Warning)

switch = GetCaseData(ConfigHandler.config_path).get_yaml_data()['MySqlDB']['switch']


class MysqlDB(object):
    if switch:

        def __init__(self):
            self.config = GetYamlData(ConfigHandler.config_path)
            self.read_mysql_config = self.config.get_yaml_data()['MySqlDB']

            try:
                # 建立数据库连接
                self.conn = pymysql.connect(
                    host=self.read_mysql_config['host'],
                    user=self.read_mysql_config['user'],
                    password=self.read_mysql_config['password'],
                    db=self.read_mysql_config['db']
                )

                # 使用 cursor 方法获取操作游标，得到一个可以执行sql语句，并且操作结果为字典返回的游标
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def __del__(self):
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def query(self, sql, state="all"):
            """
                查询
                :param sql:
                :param state:  all 是默认查询全部
                :return:
                """
            try:
                self.cur.execute(sql)

                if state == "all":
                    # 查询全部
                    data = self.cur.fetchall()

                else:
                    # 查询单条
                    data = self.cur.fetchone()

                return data
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def execute(self, sql):
            """
                更新 、 删除、 新增
                :param sql:
                :return:
                """
            try:
                # 使用 excute 操作 sql
                rows = self.cur.execute(sql)
                # 提交事务
                self.conn.commit()
                return rows
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))
                # 如果事务异常，则回滚数据
                self.conn.rollback()

        def assert_execution(self, sql: list, resp) -> dict:
            """
                执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会将所有数据以对象形式返回
                :param resp: 接口响应数据
                :param sql: sql
                :return:
                """
            try:
                if isinstance(sql, list):

                    data = {}
                    if 'UPDATE' and 'update' and 'DELETE' and 'delete' and 'INSERT' and 'insert' in sql:
                        raise "断言的 sql 必须是查询的 sql"
                    else:
                        for i in sql:
                            # 判断sql中是否有正则，如果有则通过jsonpath提取相关的数据
                            sql = SqlRegular(i, resp)
                            # for 循环逐条处理断言 sql
                            query_data = self.query(sql)[0]
                            # 将sql 返回的所有内容全部放入对象中
                            for key, value in query_data.items():
                                data[key] = value

                        return data
                else:
                    raise "断言的查询sql需要是list类型"
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))
                raise


if __name__ == '__main__':
    mydb = MysqlDB()
    a = mydb.assert_execution(sql=["select count(id) as totalCount from test_obp_order.order_sub_order where shop_id = 515"], resp={"code": 237, "value": 1})
    print(a)