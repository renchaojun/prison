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
这部分根据统计信息trafic_static_map完成数据的随机生成,并写入数据库,虚拟数据的data_type=1
1.读取统计文件trafic_static_map.json
2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
3.计算总分,按照打标签static_map中最后一项阈值,完成打标签
4.构造sql,写入数据库
"""
if __name__ == '__main__':
    # 生成1k条虚拟数据
    N = 1100
    # 1.读取统计文件drug_static_map.json
    static_map = sava_to_json.load_json(curPath.mainPath() + "/temp_file/traffic_static_map")
    print(len(static_map))

    # 2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    data = {}
    base_id = 1
    for i in range(N):
        name = pr.random_name()
        data[name] = [name]
        for key in static_map:
            if len(static_map[key]) == 4:
                data[name].append(pr.random_normal(static_map, key))

    # 3.计算总分, 按照打标签static_map中最后一项阈值, 完成打标签
    n = 0
    """
        安全驾驶态度差:
            妨碍道路畅通且不规则遵守：1-9题
            超速驾驶：10-14题
            激情驾驶：15-18题
        """
    attitude1 = np.array(range(1, 10))
    attitude2 = np.array(range(10, 15))
    attitude3 = np.array(range(15, 19))
    attitude_all = np.array(range(1, 19))
    n = n +4
    data = p.sum_score(data, attitude1, attitude2, attitude3, attitude_all)

    """
        驾驶员自我效能感,1-9反向记分
    """
    reverse_order = np.array(range(1, 10)) + 19 - 1
    data = p.reverce_score(data, reverse_order, 7)
    self = np.array(range(1, 13)) + 19 - 1
    data = p.sum_score(data, self)
    n = n + 1

    """
    多维度交通心理控制源:
        1-5题：其他驾驶员原因
        6-9题：自身原因
        10-12题：车辆和环境原因
        13-16题：命运原因
    得分越高表明在个体越容易把交通事故归结为某一因素
    """
    reason1 = np.array(range(1, 6)) + 31 - 1
    reason2 = np.array(range(6, 10)) + 31 - 1
    reason3 = np.array(range(10, 13)) + 31 - 1
    reason4 = np.array(range(13, 17)) + 31 - 1
    reason_all = np.array(range(1, 17)) + 31 - 1
    data = p.sum_score(data, reason1, reason2, reason3, reason4, reason_all)
    n = n +5

    """
    简版病理性自恋:
        得分越高表明个体的病理性自恋水平越高
    """
    pathology = np.array(range(1, 29)) + 47 - 1
    data = p.sum_score(data, pathology)
    n = n + 1

    """
    责任性量表:
        计算总分，总分越高，责任性越强
    """
    reverse_order = np.array([1, 2, 4, 5, 7, 8, 10, 12]) + 75 - 1
    data = p.reverce_score(data, reverse_order, 5)
    responsibility = np.array(range(1, 13)) + 75 - 1
    data = p.sum_score(data, responsibility)
    n = n + 1

    # ---------------------------生成数据并求维度的和完毕-------------------------------------------
    # 根据阈值计算标签
    table = np.load(curPath.mainPath() + "/traffic/traffic.npy")
    flag_map = pr.cul_flag(data, table, n, static_map["boundary_score"])

    # 4.数据写入
    config = u.ReadConfig()
    traffic_table_name = config.get_tablename("traffic_name")
    con = db.DB()
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
        if len(flag_map[key])!=0:
            sql_insert = sql_insert.format(traffic_table_name, *adata,p.join(flag_map[key]))
        else:
            sql_insert = sql_insert.format(traffic_table_name, *adata, "无")
        print(sql_insert)
        con.insert(sql_insert)