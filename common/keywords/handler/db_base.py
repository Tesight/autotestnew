import pymysql
import sqlite3

from common.container import LocalManager
from common.logger import Log
import os
import jaydebeapi
from common.comdata import CommonData
from common.utils.u_ini import read_ini_file


class MysqlBase(object):
    """Mysql数据库封装类"""

    def __init__(self, host, user, passwd, port, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = int(port)
        self.db = database
        self.connection = None

    def create_connection(self):
        """创建连接"""
        self.connection = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, port=self.port,
                                          db=self.db, charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    def db_select(self, sql):
        """数据库查询操作"""
        try:
            self.create_connection()
            with self.connection.cursor() as cursor:  # 使用with可以在执行结束后自动关闭游标
                cursor.execute(sql)
                result_set = cursor.fetchall()
            return result_set
        except Exception as e:
            Log().logger.error(u'查询错误...', e)
        finally:
            self.connection.close()

    def db_operate(self, sql):
        """增删改数据库操作"""
        try:
            self.create_connection()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                # 提交数据库事务
                self.connection.commit()
        except Exception as e:
            # 数据库事务回滚
            self.connection.rollback()
            Log().logger.error("数据库操作失败", e)
        finally:
            self.connection.close()


class SqliteBase(object):
    """Sqlite3数据库封装类"""

    def __init__(self, database=''):
        self.database = database
        self.connection = None

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_connection(self):
        """创建连接"""
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = self.dict_factory

    def db_select(self, sql):
        """数据库查询操作"""
        try:
            self.create_connection()
            cur = self.connection.cursor().execute(sql)
            result_set = cur.fetchall()
            return result_set
        except Exception as e:
            Log().logger.error(u'查询错误...', e)
        finally:
            self.connection.close()

    def db_operate(self, sql):
        """增删改数据库操作"""
        try:
            self.create_connection()
            self.connection.cursor().execute(sql)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            Log().logger.error("数据库操作失败", e)
        finally:
            self.connection.close()


class JdbcBase(object):
    """通过jdbc方式连接各种数据库"""

    def __init__(self, dbtype, host, user, passwd, port, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = int(port)
        self.database = database
        self.url, self.driver, self.jarFile = self.get_db_info(dbtype)
        self.connection = None

    def create_connection(self):
        """创建连接"""
        self.connection = jaydebeapi.connect(self.driver, self.url, [self.user, self.passwd], self.jarFile)

    def get_db_info(self, dbtype):
        dbinfo = read_ini_file(os.path.join(CommonData.DB_DRIVER, 'dbinfo.ini'))
        url = None
        if dbtype == 'sqlite':
            url = dbinfo[dbtype]['url模板'].format(dbPATH=self.database)
        else:
            if dbtype in dbinfo.keys():
                url = dbinfo[dbtype]['url模板'].format(IP=self.host, PORT=self.port, DATABASE=self.database)
            else:
                print("暂不支持此数据库：{}".format(dbtype))
        driver_class = dbinfo[dbtype]['类名']
        jar_name = os.path.join(CommonData.DB_DRIVER, dbinfo[dbtype]['添加文件'])
        return url, driver_class, jar_name

    def db_select(self, sql):
        """数据库查询操作"""
        try:
            self.create_connection()
            with self.connection.cursor() as cursor:  # 使用with可以在执行结束后自动关闭游标
                cursor.execute(sql)
                result_set = cursor.fetchall()
            return result_set
        except Exception as e:
            Log().logger.error('查询错误...', e)
        finally:
            self.connection.close()

    def db_operate(self, sql):
        """增删改数据库操作"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                self.connection.commit()
        except Exception as e:
            Log().logger.error('操作错误并回滚...', e)
            self.connection.rollback()
        finally:
            self.connection.close()


class DbAction(object):
    """全部数据库操作"""

    @staticmethod
    def _get_database_config(dbtype=None, host=None, user=None, passwd=None, port=None, database=None):
        """获取数据库配置数据"""
        db_config = {
                "dbtype": dbtype,
                "host": host,
                "user": user,
                "passwd": passwd,
                "port": port,
                "database": database
            }
        config_info = CommonData.get_config_item("数据库连接配置")
        if not dbtype:
            db_config["dbtype"] = config_info["dbtype"]
        if not dbtype:
            db_config["host"] = config_info["host"]
        if not dbtype:
            db_config["user"] = config_info["user"]
        if not dbtype:
            db_config["passwd"] = config_info["passwd"]
        if not dbtype:
            db_config["port"] = config_info["port"]
        if not dbtype:
            db_config["database"] = config_info["database"]
        Log().logger.info("获取数据库配置信息：{}".format(db_config))
        return db_config

    @staticmethod
    def _get_db_obj(db_config):
        if db_config["dbtype"] == "mysql":
            db_obj = MysqlBase(db_config["host"], db_config["user"], db_config["passwd"],
                               db_config["port"], db_config["database"])
        elif db_config["dbtype"] == "sqlite":
            db_obj = SqliteBase(db_config["database"])
        else:
            db_obj = JdbcBase(db_config["dbtype"], db_config["host"], db_config["user"],
                              db_config["passwd"], db_config["port"], db_config["database"])
        return db_obj

    @classmethod
    @LocalManager.save_result
    def db_select(cls, sql, dbtype=None, host=None, user=None, passwd=None, port=None, database=None, result='result'):
        """数据库查询"""
        db_config = cls._get_database_config(dbtype, host, user, passwd, port, database)
        db_obj = cls._get_db_obj(db_config)
        Log().logger.info("数据库查询sql：{}".format(sql))
        db_result = db_obj.db_select(sql)
        Log().logger.info(
            f'执行{cls.__name__}.db_select方法，返回值{result}==>'
            f'{dbtype}数据库查询成功：{db_result}'
        )
        return db_result

    @classmethod
    def db_operate(cls, sql, dbtype=None, host=None, user=None, passwd=None, port=None, database=None):
        """数据库操作"""
        db_config = cls._get_database_config(dbtype, host, user, passwd, port, database)
        db_obj = cls._get_db_obj(db_config)
        Log().logger.info("数据库操作sql：{}".format(sql))
        db_obj.db_operate(sql)
        Log().logger.info(
            f'执行{cls.__name__}.db_operate方法==>'
            f'{dbtype}数据库执行操作成功！'
        )


if __name__ == '__main__':
    pass
