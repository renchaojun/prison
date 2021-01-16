import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import copy
import time
import random
import datetime
import position_zw.position as p
import position_zw.random_generate as pr
"""
这部分根据统计信息drug_static_map完成数据的随机生成,并写入数据库,虚拟数据的data_type=1
1.读取统计文件drug_static_map.json
2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
3.计算总分,按照打标签static_map中最后一项阈值,完成打标签
4.构造sql,写入数据库
"""

if __name__ == '__main__':
    # 生成1k条虚拟数据
    N = 1000
    # 1.读取统计文件drug_static_map.json
    static_map = sava_to_json.load_json(curPath.mainPath() + "/temp_file/drug_static_map")

    # 2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    data = {}
    base_id = int(max(static_map["ID完整"])) + 1
    for i in range(N):
        my_id = base_id + i
        data[my_id] = [my_id]
        for key in static_map:
            if len(static_map[key])==4:
                data[base_id + i].append(pr.random_normal(static_map, key))
    # print(data)

    # 3.计算总分, 按照打标签static_map中最后一项阈值, 完成打标签
    n = 0
    """
       短式黑暗三联征:马基雅维利主义人格[1,10)
    """
    three_feature_factor = (np.array(range(1, 10)))
    # 记分求和  短式黑暗三联征:马基雅维利主义人格
    n = n + 1
    data = p.sum_score(data, three_feature_factor)
    """
        奖励/惩罚敏感性问卷
    """
    sensitive = np.array(range(1, 49, 2)) + 10 - 1  # 惩罚敏感
    sensitive2 = np.array(range(2, 49, 2)) + 10 - 1  # 奖励敏感
    data = p.sum_score(data, sensitive, sensitive2)
    n = n + 2

    """
        领悟社会支持
    """
    reverse_order = np.array([3, 4, 8, 11, 6, 7, 9, 12, 1, 2, 5, 10]) + 58 - 1
    data = p.reverce_score(data, reverse_order, 7)
    society_factory1 = np.array([3, 4, 8, 11]) + 58 - 1
    society_factory2 = np.array([6, 7, 9, 12]) + 58 - 1
    society_factory3 = np.array([1, 2, 5, 10]) + 58 - 1
    society_factory_all = np.concatenate((society_factory1, society_factory2, society_factory3), axis=0)
    data = p.sum_score(data, society_factory1, society_factory2, society_factory3, society_factory_all)
    n = n + 4

    """
        犯罪思维与同伴量表  
    """
    reverse_order = np.array([25, 28, 31, 35, 39, 41, 45]) + 70 - 1
    data = p.reverce_score(data, reverse_order, 1)
    mind = np.array((range(1, 47))) + 70 - 1
    data = p.sum_score(data, mind)
    n = n + 1

    """
        反社会人格障碍  >=3
    """
    society = np.array((range(1, 8))) + 116 - 1
    data = p.sum_score(data, society)
    n = n + 1

    #---------------------------生成数据并求维度的和完毕-------------------------------------------
    # 根据阈值计算标签
    table=np.load(curPath.mainPath() + "/drug/drug.npy")
    flag_map=pr.cul_flag(data,table,n,static_map["boundary_score"])

    # 4.数据写入
    config = u.ReadConfig()
    position_table_name = config.get_tablename("drug_name")
    con = db.DB()
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
        if len(flag_map[key])!=0:
            sql_insert = sql_insert.format(position_table_name, *adata,p.join(flag_map[key]))
        else:
            sql_insert = sql_insert.format(position_table_name, *adata, "无")
        print(sql_insert)
        con.insert(sql_insert)