from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import copy
import position_zw.position as p
"""
处理涉毒犯
1.数据读
2.数据清洗(不需要数据清洗,因为没有缺失值)
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""

def read_position_excel(config,file_name):
    drug_path=curPath.mainPath()+config.get_filename(file_name)
    workbook = load_workbook(drug_path)
    sheets = workbook.get_sheet_names()  # #四个sheet对应有四个维度,标签
    data={}   #存罪犯数据
    table=[]  #存属性
    booksheet = workbook.get_sheet_by_name(sheets[0])
    rows = booksheet.rows

    # 迭代所有的行
    num_row = 0
    for row in rows:
        if num_row == 0:
            line = [col.value for col in row]
            table=table+line
        else:
            line = [col.value for col in row]
            data[line[0]]=line
        num_row = num_row + 1

    # 不满足条件的罪犯数据删掉,此处数据很好,完备
    new_data={}
    for key in data:
        if (len(data[key]) == len(table)):
            new_data[key]=data[key]
    return table,new_data

def cul_flag(data,table,n,percent,static_map):
    """
    :param data: map
    :param table: one_dim list
    :param n: int
    :param percent: float
    :return:flag_map
    """
    all_score_arr = []
    basic_score = []  # 基准分数
    for key in data:
        adata = data[key]
        all_score_arr.append(adata[len(table) - n - 1:len(table) - 1])
    # print(all_score_arr)
    all_score_arr = np.array(all_score_arr)
    for j in range(len(all_score_arr[0])):
        if j==len(all_score_arr[0])-1:
            basic_score.append(3)
            break
        lie = all_score_arr[:, j]
        lie.sort()
        basic_score.append(lie[round(len(lie) * (1 - percent))])
    static_map["boundary_score"] = basic_score
    # print(basic_score) #得到基准分数
    flag_map = {}
    for key in data:
        adata = data[key]
        score_arr = adata[len(table) - n - 1:len(table) - 1]  # 拿出来一个罪犯的一行,计算的小维度总分
        for i in range(len(score_arr)):
            print(basic_score[i])
            if int(score_arr[i]) >= int(basic_score[i]):
                name = table[len(table) - n - 1 + i]
                if adata[0] not in flag_map:
                    flag_map[adata[0]] = []
                    flag_map[adata[0]].append(name)
                else:
                    flag_map[adata[0]].append(name)
    return flag_map, static_map

if __name__ == '__main__':
    # 1.读取总的数据表格
    file_name="drug_file"
    config = u.ReadConfig()
    table, data = read_position_excel(config,file_name)  # 得到全部的列数据和表头
    # 2.清洗数据(忽略)
    # 3.计算总分
    n=0
    """
       短式黑暗三联征:马基雅维利主义人格[1,10)
    """
    three_feature_factor = (np.array(range(1, 10)))
    # 记分求和  短式黑暗三联征:马基雅维利主义人格
    title = np.array(["短式黑暗三联征:马基雅维利主义"])
    n = n + len(title)
    data = p.sum_score(data, three_feature_factor)
    table = np.hstack((table, title))
    """
        奖励/惩罚敏感性问卷
    """
    sensitive = np.array(range(1,49,2))+10-1   #惩罚敏感
    sensitive2 = np.array(range(2,49,2))+10-1   #奖励敏感
    title2 = np.array(["个体对惩罚信息敏感","个体对奖励信息敏感"])
    data = p.sum_score(data, sensitive,sensitive2)
    table = np.hstack((table, title2))
    n = n + len(title2)

    """
        领悟社会支持
    """
    reverse_order = np.array([3, 4, 8, 11, 6, 7, 9, 12, 1, 2, 5, 10]) +58-1
    data = p.reverce_score(data, reverse_order, 7)
    society_factory1 = np.array([3, 4, 8, 11]) + 58 - 1
    society_factory2 = np.array([6, 7, 9, 12]) + 58 - 1
    society_factory3 = np.array([1, 2, 5, 10]) + 58 - 1
    society_factory_all = np.concatenate((society_factory1, society_factory2, society_factory3), axis=0)
    title3 = np.array(["领悟社会支持:缺乏家庭支持", "领悟社会支持:缺乏朋友支持", "领悟社会支持:缺乏其他支持", "个体整体的社会支持低"])
    data = p.sum_score(data, society_factory1, society_factory2, society_factory3, society_factory_all)

    table = np.hstack((table, title3))
    n = n + len(title3)

    """
        犯罪思维与同伴量表  
    """
    reverse_order = np.array([25,28,31,35,39,41,45])+70-1
    data = p.reverce_score(data, reverse_order, 1)
    mind=np.array((range(1,47)))+70-1
    title4=np.array(["犯罪思维与同伴量表"])
    data = p.sum_score(data, mind)
    table = np.hstack((table, title4))
    n = n + len(title4)

    """
        反社会人格障碍  >=3
    """
    society=np.array((range(1,8)))+116-1
    title5=np.array(["反社会人格障碍"])
    data = p.sum_score(data, society)
    table = np.hstack((table, title5))
    n = n + len(title5)

    # 3.5打标签之前做一次统计,并存入表格,便于后续生成其他的数据
    # 生成统计意义上的{feature:均值,方差,min,max,基本信息:[基本信息集合],维度的标签阈值:[即大维度和小维度的得分阈值界限,超过即需要打标签]}
    static_map = {}
    static_map = p.static(static_map, data, table, 0, 1, 1, 123)
    # 返回static_map后,还差各个大小维度总和的阈值,在步骤4中添加

     #4.打标签
    table = np.hstack((table, np.array(["标签"])))
    flag_map, static_map = cul_flag(data, table, n, 0.27, static_map)

    # 5.建表
    drug_table_name = config.get_tablename("drug_name")
    sql_createTb = "create table {} (id int primary key auto_increment,data_type int(1) ,`{}`char(20) not null default ''," + "`{}` char(20) not null default ''," * (
                len(table) - 2) + "{} text(500))CHARSET=utf8;"
    sql_createTb = sql_createTb.format(drug_table_name, *table)
    print(table)
    print(sql_createTb)
    con = db.DB()
    con.chech_table_exit(drug_table_name, sql_createTb)

    # 6.数据写入
    data_arr = []
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,0," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert = sql_insert.format(drug_table_name, *adata, p.join(flag_map[key]))
        except:
            sql_insert = sql_insert.format(drug_table_name, *adata, "无")
        print(sql_insert)
        # con.insert(sql_insert)
    # print(data)  # {key(编号),value:数据}

    # 7.保存table用于提供web接口
    np.save(curPath.mainPath() + "/drug/drug.npy", table)
    # 3.5+4步骤中的数据static_map进行保存
    sava_to_json.save_json(static_map, curPath.mainPath() + "/temp_file/drug_static_map")