from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import copy
import position_zw.position as p
import drug.read_drug as d
"""
处理交通肇事罪
1.数据读
2.数据清洗(不需要数据清洗,因为没有缺失值)
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""
if __name__ == '__main__':
    # 1.读取总的数据表格
    file_name = "traffic_file"
    config = u.ReadConfig()
    table, data = d.read_position_excel(config, file_name)  # 得到全部的列数据和表头

    # 2.清洗数据(忽略)
    # 3.计算总分
    n = 0
    """
    安全驾驶态度差:
        妨碍道路畅通且不规则遵守：1-9题
        超速驾驶：10-14题
        激情驾驶：15-18题
    """
    attitude1=np.array(range(1,10))
    attitude2=np.array(range(10,15))
    attitude3=np.array(range(15,19))
    attitude_all=np.array(range(1,19))
    title = np.array(["安全驾驶态度:妨碍道路畅通且不规则遵守","安全驾驶态度:超速驾驶","安全驾驶态度:激情驾驶","整体安全驾驶态度差"])
    n = n + len(title)
    data = p.sum_score(data, attitude1,attitude2,attitude3,attitude_all)
    table = np.hstack((table, title))

    """
        驾驶员自我效能感,1-9反向记分
    """
    reverse_order = np.array(range(1,10)) +19-1
    data = p.reverce_score(data, reverse_order, 7)
    self=np.array(range(1,13)) +19-1
    title2 = np.array(["驾驶员自我效能感差"])
    data = p.sum_score(data,self)
    table = np.hstack((table, title2))
    n = n + len(title2)

    """
    多维度交通心理控制源:
        1-5题：其他驾驶员原因
        6-9题：自身原因
        10-12题：车辆和环境原因
        13-16题：命运原因
    得分越高表明在个体越容易把交通事故归结为某一因素
    """
    reason1 = np.array(range(1, 6)) + 31 - 1
    reason2 = np.array(range(6,10)) + 31 - 1
    reason3 = np.array(range(10, 13)) + 31 - 1
    reason4 = np.array(range(13, 17)) + 31 - 1
    reason_all = np.array(range(1, 17)) + 31 - 1
    title3 = ["个体越容易把交通事故归结为其他驾驶员原因",
              "个体越容易把交通事故归结为自身原因",
              "个体越容易把交通事故归结为车辆和环境原因",
              "个体越容易把交通事故归结为命运原因",
              "个体越容易把交通事故归结为某一因素"]
    data = p.sum_score(data, reason1,reason2,reason3,reason4,reason_all)
    table = np.hstack((table, title3))
    n = n + len(title3)

    """
    简版病理性自恋:
        得分越高表明个体的病理性自恋水平越高
    """
    pathology=np.array(range(1,29))+47-1
    title4=["个体的病理性自恋水平高"]
    data = p.sum_score(data, pathology)
    table = np.hstack((table, title4))
    n = n + len(title4)

    """
    责任性量表:
        计算总分，总分越高，责任性越强
    """
    reverse_order = np.array([1,2,4,5,7,8,10,12]) + 75 - 1
    data = p.reverce_score(data, reverse_order,5)
    responsibility=np.array(range(1,13))+75-1
    title5=["责任性差"]
    data = p.sum_score(data, responsibility)
    table = np.hstack((table, title5))
    n = n + len(title5)

    # 3.5打标签之前做一次统计,并存入表格,便于后续生成其他的数据
    # 生成统计意义上的{feature:均值,方差,min,max,基本信息:[基本信息集合],维度的标签阈值:[即大维度和小维度的得分阈值界限,超过即需要打标签]}
    static_map = {}
    static_map = p.static(static_map, data, table, 0, 1, 1, 87)
    # 返回static_map后,还差各个大小维度总和的阈值,在步骤4中添加

    # 4.打标签
    table = np.hstack((table, np.array(["标签"])))
    flag_map, static_map = p.cul_flag(data, table, n, 0.27, static_map)

    # 5.建表
    traffic_table_name = config.get_tablename("traffic_name")
    sql_createTb = "create table {} (id int primary key auto_increment,data_type int(1) ,`{}`char(20) not null default ''," + "`{}` char(20) not null default ''," * (
            len(table) - 2) + "{} text(1000))CHARSET=utf8;"
    sql_createTb = sql_createTb.format(traffic_table_name, *table)
    print(table)
    print(sql_createTb)
    con = db.DB()
    con.chech_table_exit(traffic_table_name, sql_createTb)

    # 6.数据写入
    data_arr = []
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,0," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert = sql_insert.format(traffic_table_name, *adata, p.join(flag_map[key]))
        except:
            sql_insert = sql_insert.format(traffic_table_name, *adata, "无")
        print(sql_insert)
        con.insert(sql_insert)
    # print(data)  # {key(编号),value:数据}

    # 7.保存table用于提供web接口
    np.save(curPath.mainPath() + "/traffic/traffic.npy", table)
    # 3.5+4步骤中的数据static_map进行保存
    sava_to_json.save_json(static_map, curPath.mainPath() + "/temp_file/traffic_static_map")