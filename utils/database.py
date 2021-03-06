import mysql.connector
import utils.parse_config as u
class DB():
    def __init__(self):
        self.config = u.ReadConfig()
        self.host=self.config.get_db("host")
        self.user=self.config.get_db("user")
        self.password=self.config.get_db("password")
        self.database=self.config.get_db("database")
    def get_connetion(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            database=self.database
        )
    def chech_table_exit(self,table_name,sql_createTb):
        """
        检查表格是否存在,不存在则创建表格
        :param table_name: 表名
        :param sql_createTb: 建表语句
        :return:
        """
        mydb=self.get_connetion()
        mycursor = mydb.cursor()
        mycursor.execute("SHOW TABLES")  ##查看表是否存在
        flag = False
        for x in mycursor:
            if x[0] == table_name:
                flag = True
        if not flag:
            mycursor.execute(sql_createTb)
            print("建表{}完成!".format(table_name))
        mydb.close()
    def insert(self,sql):
        mydb = self.get_connetion()
        mycursor = mydb.cursor()
        try:
            mycursor.execute(sql)
            mydb.commit()
        except Exception:  # 方法一：捕获所有异常
            # 如果发生异常，则回滚
            print("发生异常", Exception)
            mydb.rollback()
        mydb.close()
    def select(self,sql):
        mydb = self.get_connetion()
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        data=mycursor.fetchall()
        mydb.commit()
        mydb.close()
        return data
    def add(self,sql): #查看是否含有描述那列
        mydb = self.get_connetion()
        mycursor = mydb.cursor()
        try:
            mycursor.execute(sql)
            mydb.commit()
            print("添加列成功")
        except Exception:  # 方法一：捕获所有异常
            # 如果发生异常，则回滚
            print("发生异常", Exception)
            mydb.rollback()
        mydb.close()
    def updata(self,sql): #查看是否含有描述那列
        mydb = self.get_connetion()
        mycursor = mydb.cursor()
        try:
            mycursor.execute(sql)
            mydb.commit()
            print("更新成功")
        except Exception:  # 方法一：捕获所有异常
            # 如果发生异常，则回滚
            print("发生异常", Exception)
            mydb.rollback()
        mydb.close()