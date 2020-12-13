from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
"""
处理盗窃犯
1.数据读
2.数据清洗
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""
def read_thieves_excel(config):
    thieves_path=config.get_filename("thieves_file")
    workbook = load_workbook(thieves_path)
    sheets = workbook.get_sheet_names()  # #四个sheet对应有四个维度,标签
    # print(sheets)
    sheet_size=len(sheets)
    data={}
    table=[]
    for i in range(sheet_size):  #145列/289列/433列/577列
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
                    table=table+line[1:]
                num_row =num_row +1
            else:
                line = [col.value for col in row]
                if line[0] not in data:
                    data[line[0]]=line
                else:
                    data[line[0]]=data[line[0]]+line[1:]
                num_row = num_row + 1

        if i==3:
            # print(table)
            # print(data)
            # print(len(table))
            # print(len(data["14637李芸"]))
            break

    # 不满足条件的罪犯数据删掉
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
    #前面基本信息 [0:11]不处理,
    for j in range(len(arr[0])):
        if  (j>=11 and j<143) or (j>=146 and j<162) or (j>=163 and j<175)or (j>=176 and j<238):
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
def reverce_score_bool(data,reverse_order):
    for key in data:
        adata=data[key]
        for i in reverse_order:
            adata[i]=1-adata[i]
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
    table,data=read_thieves_excel(config) #得到全部的列数据和表头

    """
    基本信息 [0:11]
    父母教养方式:[11:143]
    自我控制量表:[146:162]
    领悟社会支持:[163:175]
    应对方式问卷:[176:238]
    """
    # 2.数据清洗
    data=wash_process(data)  #
    # print(data)


    #共几个小维度
    n=0
    # 3.计算维度得分
    # 父母教养方式**************************************************************************
    father_factor1=(np.array([2,4,6,7,9,15,20,25,29,30,31,32,33,37,42,54,60,61,66])-1)*2+11
    mother_factor1=(np.array([2,4,6,7,9,15,25,29,30,31,32,33,37,42,44,54,60,61,63])-1)*2+12
    father_factor2=(np.array([1,10,11,14,27,36,48,50,56,57])-1)*2+11
    mother_factor2=(np.array([1,11,12,14,16,19,24,27,35,36,41,48,50,56,57,59])-1)*2+12
    father_factor3=(np.array([21,23,28,34,35,45])-1)*2+11
    mother_factor3=(np.array([23,26,28,34,38,39,45,47])-1)*2+12
    father_factor4=(np.array([5,13,17,18,43,49,51,52,53,55,58,62])-1)*2+11
    mother_factor4=(np.array([13,17,43,51,52,53,55,58,62])-1)*2+12
    father_factor5=(np.array([3,8,22,64,65])-1)*2+11
    mother_factor5=(np.array([3,8,22,64,65])-1)*2+12
    father_factor6 = (np.array([3, 8, 22, 64, 65]) - 1) * 2 + 11
    # print(data["14637李芸"][176:238])
    # 记分求和  父母教养方式
    title=np.array(["家庭教养方式:父亲情感温暖与理解关心","家庭教养方式:母亲情感温暖与理解关心",
           "家庭教养方式:父亲过分干涉","家庭教养方式:母亲过度干涉",
           "家庭教养方式:父亲拒绝与否认","家庭教养方式:母亲拒绝与否认",
           "家庭教养方式:父亲惩罚严厉","家庭教养方式:母亲惩罚严厉",
           "家庭教养方式:父亲偏爱被试","家庭教养方式:母亲偏爱被试",
           "家庭教养方式:父亲过度保护",
           ])
    n=n+len(title)
    data=sum_score(data,father_factor1,mother_factor1,father_factor2,mother_factor2,
              father_factor3,mother_factor3,father_factor4,mother_factor4,father_factor5,
              mother_factor5,father_factor6)
    table=np.hstack((table,title))


    # 自我控制量表**************************************************************************
    reverse_order=np.array([2,3,9,12,15,16])+146-1
    data=reverce_score(data,reverse_order)
    control_factor1=np.array([1,10,5,14])+146-1
    control_factor2=np.array([4,13,15,16,6,11])+146-1
    control_factor3=np.array([2,12,3,7,8,9])+146-1
    title2=np.array(["自我控制:冲动冒险","自我控制:情绪性","自我控制:简单倾向"])
    data=sum_score(data,control_factor1,control_factor2,control_factor3)
    table = np.hstack((table, title2))
    n=n+len(title2)

    # 领悟社会支持**************************************************************************
    society_factory1=np.array([3,4,8,11])+163-1
    society_factory2=np.array([6,7,9,12])+163-1
    society_factory3=np.array([1,2,5,10])+163-1
    title3 = np.array(["领悟社会支持:家庭支持", "领悟社会支持:朋友支持", "领悟社会支持:其他支持"])
    data = sum_score(data, society_factory1, society_factory2, society_factory3)
    table = np.hstack((table, title3))
    n=n+len(title3)

    # 应对方式问卷**************************************************************************
    reverse_order = np.array([1,2,3,5,8,19,29,31,40,46,51,55,10,11,14,36,39,48,50,56,57,59]) + 176 - 1
    data = reverce_score_bool(data, reverse_order)
    process_factory1 = np.array([1,2,3,5,8,19,29,31,40,46,51,55]) + 176 - 1
    process_factory2 = np.array([15,23,25,37,48,50,56,57,59]) + 176 - 1
    process_factory3 = np.array([10,11,14,36,39,48,50,56,57,59]) + 176 - 1
    process_factory4 = np.array([4,12,17,21,22,26,28,41,45,49]) + 176 - 1
    process_factory5 = np.array([7,13,16,19,24,27,32,34,35,44,47]) + 176 - 1
    process_factory6 = np.array([6,9,18,20,30,33,38,52,54,58,61]) + 176 - 1
    title4 = np.array(["应对方式:不擅长解决问题","应对方式:自责","应对方式:不擅长求助","应对方式:幻想","应对方式:退避","应对方式:合理化"])
    data = sum_score(data, process_factory1, process_factory2, process_factory3,process_factory4,process_factory5,process_factory6)
    table = np.hstack((table, title4))
    n=n+len(title4)


    # 4.打标签
    table=np.hstack((table, np.array(["标签"])))
    flag_map=cul_flag(data,table,n,0.27)
    print("共计算了{}个小维度".format(n))
    # print("每个犯人的标签:",flag_map)


    #5.建表
    thieves_table_name=config.get_tablename("thieves_name")
    table=process_empty(table)
    sql_createTb="create table {} (id int primary key auto_increment,`{}`char(10) not null default '',"+"`{}` char(8) not null default '',"*(len(table)-2) +"{} char(255) not null default '')CHARSET=utf8;"
    sql_createTb=sql_createTb.format(thieves_table_name,*table)
    # print(sql_createTb)
    con=db.DB()
    con.chech_table_exit(thieves_table_name,sql_createTb)
    #6.数据写入
    data_arr=[]
    # print(len(table))
    # print(flag_map)
    for key in data:
        adata=data[key]
        sql_insert = "insert into {} values(default," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert=sql_insert.format(thieves_table_name,*adata,join(flag_map[key]))
        except:
            sql_insert=sql_insert.format(thieves_table_name,*adata,"无")
        print(sql_insert)
        # con.insert(sql_insert)
    # print(data)
    # print(len(table))

    # 7.保存table用于提供web接口
    np.save("thieves.npy", table)