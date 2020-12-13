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
        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
    def select(self,sql):
        mydb = self.get_connetion()
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        data=mycursor.fetchall()
        mydb.commit()
        mydb.close()
        return data