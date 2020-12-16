import configparser
import os
class ReadConfig:
    def __init__(self, filepath=None):
        if filepath:
            configpath = filepath
        else:
            root_dir = os.path.abspath('.')
            configpath = os.path.join(root_dir, "config.ini")
        self.cf = configparser.ConfigParser()
        self.cf.read(configpath)

    def get_db(self, param):
        value = self.cf.get("Mysql-Database", param)
        return value
    def get_filename(self, param):
        value = self.cf.get("File-name", param)
        return value
    def get_tablename(self,param):
        return self.cf.get("Table-name",param)
if __name__ == '__main__':
    test = ReadConfig()
    t = test.get_db("host")
    t2 = test.get_filename("thieves_file")
    print(t)
    print(t2)