from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
import curPath
import copy
import utils.save_to_json as sava_to_json
import position_zw.position as p
"""
处理诈骗犯
1.数据读
2.数据清洗
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""
def read_fraudsters_excel(config):
    thieves_path=curPath.mainPath()+config.get_filename("fraudsters_file")
    workbook = load_workbook(thieves_path)
    sheets = workbook.get_sheet_names()  # #四个sheet对应有四个维度,标签
    # print(sheets)
    sheet_size=len(sheets)
    data={}
    table=[]
    for i in range(sheet_size):  #先算好标签
        booksheet = workbook.get_sheet_by_name(sheets[i])
        rows = booksheet.rows
        # 迭代所有的行
        num_row = 0
        for row in rows:
            if num_row == 0:
                line = [col.value for col in row]
                if i==0:
                    table=table+line
                else:
                    table=table+line[3:]
                num_row =num_row +1
    print(table)
    print(len(table))  #16+21  -3
    for i in range(sheet_size):  #再计算里面的数据
        booksheet = workbook.get_sheet_by_name(sheets[i])
        rows = booksheet.rows
        num_row=0
        for row in rows:
            if num_row != 0:
                line = [col.value for col in row]
                # print(line)
                if line[0] not in data:
                    data[line[0]]=[]
                    if i==0:
                        data[line[0]]+=(line+[-1 for _ in range(len(table)-len(line))])
                    else:
                        data[line[0]]+=(line[:3]+[-1 for _ in range(len(table)-len(line))]+line[3:])
                else:
                    data[line[0]]=data[line[0]][:16]+line[3:]

            num_row = num_row + 1
    # for key in data:
    #     print(data[key], len(data[key]))


    return table,data
def wash_process(data):
    """
    :param data: map
    :return:
    """
    arr=[] #全部存入arr
    for key in data:
        arr.append(data[key])
    arr=np.asarray(arr)
    #前面基本信息 [0:11]不处理,
    for j in range(len(arr[0])):
        if  (j>=3 and j<16) or (j>=16 and j<34):
            lie=arr[:,j]
            sum=0
            num=0
            for i in range(len(lie)):
                # if type(lie[i])==int:
                if type(lie[i])==int:
                    num=num+1
                    # print(lie[i])
                    sum=sum+int(lie[i])
            if num!=0:
                ave=round(sum/num)
            for i in range(len(lie)):
                if type(lie[i])!=int:
                    arr[i][j]=ave  #替换完成
    # 把arr的数据放入data
    for line in arr:
        data[line[0]]=line
    return data

def sum_score(data,*items):
    """
    :param data: map
    :param items: tuple
    :return:
    """
    # print(items)
    for key in data:
        inner_arr=[] #一个犯人的得分
        adata=data[key]
        for i in range(len(items)):
            sum=0
            for j in items[i]:
                if adata[j]!=-1:
                    sum+=adata[j]
                else:
                    break
            inner_arr.append(sum)
        data[adata[0]]=np.hstack((data[adata[0]],np.array(inner_arr)))

    #处理inner_arr 进行评估是否含有这个标签
    return data

def cul_flag(data,table,n,percent,static_map):
    """
    :param data: map
    :param table: one_dim list
    :param n: int
    :param percent: float
    :return:flag_map
    """
    #添加到data的总分数矩阵   一共打了2个标签
    all_score_arr=[]
    basic_score=[] #基准分数
    for key in data:
        adata=data[key]
        all_score_arr.append(adata[len(table)-n-1:len(table)-1])
    # print(all_score_arr)
    all_score_arr=np.array(all_score_arr)
    for j in range(len(all_score_arr[0])):
        lie=all_score_arr[:,j]
        lie.sort()
        if lie[0]==-1:
            basic_score.append(-1)
        else:
            basic_score.append(lie[round(len(lie)*(1-percent))])
    static_map["boundary_score"] = basic_score
    # print(basic_score) #得到基准分数
    flag_map={}
    for key in data:
        adata = data[key]
        score_arr=adata[len(table) - n - 1:len(table) - 1] #拿出来一个罪犯的一行,计算的小维度总分
        for i in range(len(score_arr)):
            if score_arr[i]>=basic_score[i]:
                name = table[len(table) - n - 1 + i]
                if adata[0] not in flag_map:
                    flag_map[adata[0]]=[]
                    flag_map[adata[0]].append(name)
                else:
                    flag_map[adata[0]].append(name)
    return flag_map,static_map
def sum_score(data,*items):
    """
    :param data: map
    :param items: tuple
    :return:
    """
    # print(items)
    for key in data:
        inner_arr=[] #一个犯人的得分
        adata=data[key]
        for i in range(len(items)):
            sum=0
            for j in items[i]:
                if adata[j]!=-1:
                    sum+=adata[j]
                else:
                    break
            inner_arr.append(sum)
        data[adata[0]]=np.hstack((data[adata[0]],np.array(inner_arr)))

    #处理inner_arr 进行评估是否含有这个标签
    return data
def join(arr):
    s=""
    for i in arr:
        s+=str(i)
        s+=";"
    return s

def static(static_map,data_map,table,start_basic,end_basic,start_form,end_form):
    """
    统计基本信息的集合以及数据的均值和标准差
    :param static_map:
    :param data_map:数据map[每个犯人编号:罪犯数据]
    :param table:数据的title
    :param start_basic:基本数据的开始
    :param end_basic:基本数据的结束+1
    :param start_form:表格问卷的开始
    :param end_form:表格问卷的结束+1
    :return:static_map  添加后返回
    """
    for i in range(start_basic,end_basic):#某列
        info=list()
        for key in data_map:
            info.append(data_map[key][i])
        static_map[table[i]]=copy.deepcopy(info)
    for i in range(start_form,end_form):
        arr=list()
        for key in data_map:
            if data_map[key][i]!=-1:
                arr.append(data_map[key][i])
        # print(arr)
        static_map[table[i]]=p.mean_and_std_min_max(np.array(arr))
    return static_map

if __name__=="__main__":
    #1.读取总的数据表格
    config=u.ReadConfig()
    table,data=read_fraudsters_excel(config) #得到全部的列数据和表头
    """
    16+21 两个量表的列
    基本信息:[0:3]
    恶意创造力:[3:16]
    马氏+自恋:[16:34]
    """

    # 2.数据清洗
    data = wash_process(data)
    # 3.计算维度得分
    n=0
    factory1=(np.array(range(4,16)))  #只打第一个标签
    factory2=(np.array(range(16,34))) #只打第二个标签
    title=np.array(['恶意创造力','马氏+自恋'])
    n+=len(title)
    data=sum_score(data,factory1,factory2)
    table=np.hstack((table,title))

    # 3.5打标签之前做一次统计,并存入表格,便于后续生成其他的数据
    # 生成统计意义上的{feature:均值,方差,min,max,基本信息:[基本信息集合],维度的标签阈值:[即大维度和小维度的得分阈值界限,超过即需要打标签]}
    static_map = {}
    static_map = static(static_map, data, table, 0, 4, 4, 36)
    # 返回static_map后,还差各个大小维度总和的阈值,在步骤4中添加

    # 4.打标签
    table=np.hstack((table, np.array(["标签"])))
    flag_map,static_map=cul_flag(data,table,n,0.27,static_map)
    # print(flag_map)
    # print(data)


    # 5.建表
    fraudsters_table_name=config.get_tablename("fraudsters_name")
    sql_createTb = "create table {} (id int primary key auto_increment,data_type int(1) ,`{}`char(10) not null default ''," + "`{}` char(10) not null default ''," * (
                len(table) - 2) + "{} char(255) not null default '')CHARSET=utf8;"
    sql_createTb = sql_createTb.format(fraudsters_table_name, *table)
    # print(sql_createTb)
    con = db.DB()
    con.chech_table_exit(fraudsters_table_name, sql_createTb)
    # 6.数据写入
    data_arr = []
    # print(len(table))
    # print(flag_map)
    for key in data:
        adata = data[key]
        sql_insert = "insert into {} values(default,0," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert = sql_insert.format(fraudsters_table_name, *adata, join(flag_map[key]))
        except:
            sql_insert = sql_insert.format(fraudsters_table_name, *adata, "无")
        print(sql_insert)
        # con.insert(sql_insert)

    #7.保存table用于提供web接口
    np.save(curPath.mainPath()+"/fraudsters_zp/fraudsters.npy", table)
    sava_to_json.save_json(static_map,curPath.mainPath()+"/temp_file/fraudsters_static_map")