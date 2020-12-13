from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
"""
处理职务犯
1.数据读
2.数据清洗
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""
def read_position_excel(config):
    position_path=config.get_filename("position_file")
    workbook = load_workbook(position_path)
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
def wash_process(data):
    """
    :param data: map
    :return:
    """
    arr=[] #全部存入arr
    for key in data:
        arr.append(data[key])
    arr=np.asarray(arr)
    # print(arr)
    #前面基本信息 [0:31]不处理,
    for j in range(len(arr[0])):
        if  j>=31:
            lie=arr[:,j]
            sum=0
            num=0
            for i in range(len(lie)):
                # if type(lie[i])==int:
                if type(lie[i])==int:
                    num=num+1
                    # print(lie[i])
                    sum=sum+int(lie[i])
            ave=round(sum/num)
            for i in range(len(lie)):
                if type(lie[i])!=int :
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
                sum+=adata[j]
            inner_arr.append(sum)
        data[adata[0]]=np.hstack((data[adata[0]],np.array(inner_arr)))

    #处理inner_arr 进行评估是否含有这个标签
    return data

def reverce_score(data,reverse_order):
    for key in data:
        adata=data[key]
        for i in reverse_order:
            adata[i]=5-adata[i]
    return data

def cul_flag(data,table,n,percent):
    """
    :param data: map
    :param table: one_dim list
    :param n: int
    :param percent: float
    :return:flag_map
    """
    #添加到data的总分数矩阵   一共打了23个标签
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
        basic_score.append(lie[round(len(lie)*(1-percent))])
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
    return flag_map
def process_empty(table):
    num=0
    for i in range(len(table)):

        if table[i]==None:
            table[i]="空白栏{}".format(num)
            num=num+1
        if i>=11 and i<143:
            table[i]="教养"+table[i]
        elif i>=145 and i<162:
            table[i] = "控制" + str(table[i])
        elif i>=162 and i<175:
            table[i] = "领悟" + str(table[i])
        elif i>=176 and i<238:
            table[i] = "应对" +str(table[i])
    return table
def join(arr):
    s=""
    for i in arr:
        s+=str(i)
        s+=";"
    return s
if __name__=="__main__":
    #1.读取总的数据表格
    config=u.ReadConfig()
    table,data=read_position_excel(config) #得到全部的列数据和表头


    """总
    基本信息 [0:31]
    量表数据 [31:124]
    """
    # 2.数据清洗
    data=wash_process(data)

    #共几个小维度
    n=0
    # 3.计算维度得分
    # 短式黑暗三联征**************************************************************************
    """
    短式黑暗三联征:
    """
    reverse_order = np.array([11,16,20,24,26]) + 31 - 1
    data = reverce_score(data, reverse_order)

    three_feature_factor1=(np.array(range(1,10)))+31-1
    three_feature_factor2=(np.array(range(10,19)))+31-1
    three_feature_factor3=(np.array(range(19,28)))+31-1
    # 记分求和  短式黑暗三联征
    title=np.array(["短式黑暗三联征:马基雅维利主义","短式黑暗三联征:精神病态","短式黑暗三联征:自恋"])
    n=n+len(title)
    data=sum_score(data,three_feature_factor1,three_feature_factor2,three_feature_factor3)
    table=np.hstack((table,title))

    #责任性量表**************************************************************************
    reverse_order=np.array([1,2,4,5,7,8,10,12])+58-1
    data=reverce_score(data,reverse_order)
    responsibility_factor1=np.array(range(28,40))++31-1
    title2=np.array(["责任感差"])
    data=sum_score(data,responsibility_factor1)
    table = np.hstack((table, title2))
    n=n+len(title2)

    # # 心理特权感量表**************************************************************************
    reverse_order = np.array([5]) + 70 - 1
    data = reverce_score(data, reverse_order)
    psychological_factory1=np.array(range(1,10))+70-1
    title3 = np.array(["心理特权感水平高"])
    data = sum_score(data, psychological_factory1)
    table = np.hstack((table, title3))
    n=n+len(title3)

    ## 物质主义价值观**************************************************************************
    reverse_order = np.array([2,3,5,6,10]) + 79 - 1
    data = reverce_score(data, reverse_order)
    money_factory1 = np.array([1,3,4,6,8]) + 79 -1
    money_factory2 = np.array([2,5,9,11,13]) + 79 -1
    money_factory3 = np.array([7,10,12]) + 79 -1
    title4 = np.array(["物质主义价值观:以财物定义成功","物质主义价值观:以获取财物为中心","求物质主义价值观:通过获取财物追求幸福"])
    data = sum_score(data, money_factory1,money_factory2,money_factory3)
    table = np.hstack((table, title4))
    n=n+len(title4)

    # 道德推脱**************************************************************************
    moral_factory1 = np.array([18,22,24,29]) + 92 - 1
    moral_factory2 = np.array([12,14,17,32]) + 92 - 1
    moral_factory3 = np.array([4,21,23,27]) + 92 - 1
    moral_factory4 = np.array([1,5,20,26]) + 92 - 1
    moral_factory5 = np.array([6,13,16,30]) + 92 - 1
    moral_factory6 = np.array([7,9,11,25]) + 92 - 1
    moral_factory7 = np.array([3,10,15,19]) + 92 - 1
    moral_factory8 = np.array([2,8,28,31]) + 92 - 1
    title5 = np.array(["道德推脱:道德辩护", "道德推脱:委婉标签", "道德推脱:有利比较",
                       "道德推脱:责任转移", "道德推脱:责任分散", "道德推脱:扭曲结果",
                       "道德推脱:责备归因", "道德推脱:非人性化",
                       ])
    data = sum_score(data, moral_factory1, moral_factory2, moral_factory3,moral_factory4,moral_factory5,
                     moral_factory6,moral_factory7,moral_factory8)
    table = np.hstack((table, title5))
    n = n + len(title5)
    # 4.打标签
    table=np.hstack((table, np.array(["标签"])))
    flag_map=cul_flag(data,table,n,0.27)
    print("共计算了{}个小维度".format(n))

    # print("每个犯人的标签:",flag_map)


    #5.建表
    position_table_name=config.get_tablename("position_name")
    sql_createTb="create table {} (id int primary key auto_increment,`{}`char(20) not null default '',"+"`{}` char(20) not null default '',"*(len(table)-2) +"{} text(1000))CHARSET=utf8;"
    sql_createTb=sql_createTb.format(position_table_name,*table)
    print(table)
    print(sql_createTb)
    con=db.DB()
    con.chech_table_exit(position_table_name,sql_createTb)

    #6.数据写入
    data_arr=[]
    # print(len(table))
    # print(flag_map)
    for key in data:
        adata=data[key]
        sql_insert = "insert into {} values(default," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert=sql_insert.format(position_table_name,*adata,join(flag_map[key]))
        except:
            sql_insert=sql_insert.format(position_table_name,*adata,"无")
        print(sql_insert)
        # con.insert(sql_insert)
    print(data)
    print(len(table))

    # 7.保存table用于提供web接口
    np.save("position.npy", table)