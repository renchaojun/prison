import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import copy
import time
import random
import datetime
import fraudsters_zp.read_fraudsters as f
import thieves_dq.random_generate as th_random
import position_zw.position as p
import position_zw.random_generate as pr
"""
这部分根据统计信息thieves_static_map完成数据的随机生成,并写入数据库,虚拟数据的data_type=1
1.读取统计文件thieves_static_map.json, -1并未参与到统计中
2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    注意的是两个属性只能生成一种属性,所以可以使用一个随机数决定创造力还是马式
3.计算总分,按照打标签static_map中最后一项阈值,完成打标签
4.构造sql,写入数据库
"""
if __name__ == '__main__':
    # 生成1k条虚拟数据
    N = 1100
    # 1.读取统计文件position_static_map.json
    static_map = sava_to_json.load_json(curPath.mainPath() + "/temp_file/fraudsters_static_map")
    print(len(static_map))

    # 2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    data = {}
    base_id = max(static_map["罪犯编号"]) + 1
    for i in range(N):
        id=base_id + i
        data[id] = []
        data[id].append(id) #"罪犯编号"
        data[id].append(random.choice(static_map["队别"]))
        data[id].append(pr.random_name())
        data[id].append(random.choice(static_map["受教育"]))
        data[id].append(random.choice(static_map["年龄"]))
        flag=random.choice(range(2))
        if flag==0:
            #12个维度
            keys=["题1","题2","题3","题4","题5","题6","题7","题8","题9","题10","题11","题12"]
            for key in keys:
                data[id].append(pr.random_normal(static_map,key))
            # 18个维度
            for i in range(18):
                data[id].append(-1)
        else:
            # 12个维度
            for i in range(12):
                data[id].append(-1)
            #18个维度
            keys=["马氏1","马氏2","马氏3","马氏4","马氏5","马氏6","马氏7","马氏8","马氏9",
                  "自恋1", "自恋2", "自恋3", "自恋4", "自恋5", "自恋6", "自恋7", "自恋8", "自恋9",]
            for key in keys:
                data[id].append(pr.random_normal(static_map,key))

    # 3.计算总分, 按照打标签static_map中最后一项阈值, 完成打标签
    n = 0
    factory1 = (np.array(range(5, 17)))  # 只打第一个标签
    factory2 = (np.array(range(17, 35)))  # 只打第二个标签
    n +=2
    data = f.sum_score(data, factory1, factory2)
    #---------------------------生成数据并求维度的和完毕-------------------------------------------
    # 根据阈值计算标签
    table = np.load(curPath.mainPath() + "/fraudsters_zp/fraudsters.npy")
    flag_map = pr.cul_flag(data, table, n, static_map["boundary_score"])

    # 4.数据写入
    config = u.ReadConfig()
    fraudsters_table_name = config.get_tablename("fraudsters_name")
    con = db.DB()
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
        if len(flag_map[key])!=0:
            sql_insert = sql_insert.format(fraudsters_table_name, *adata, p.join(flag_map[key]))
        else:
            sql_insert = sql_insert.format(fraudsters_table_name, *adata, "无")
        print(sql_insert)
        con.insert(sql_insert)


