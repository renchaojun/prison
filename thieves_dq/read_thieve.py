from openpyxl import load_workbook
import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import position_zw.position as p
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
    thieves_path=curPath.mainPath()+config.get_filename("thieves_file")
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
        if  (j>=12 and j<144) or (j>=147 and j<163) or (j>=164 and j<176)or (j>=177 and j<239):
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
                try:
                    sum+=adata[j]
                except:
                    pass
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
    static_map["boundary_score"]=basic_score
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
def process_empty(table):
    num=0
    for i in range(len(table)):
        if table[i]==None:
            table[i]="空白栏{}".format(num)
            num=num+1
        if i>=12 and i<144:
            table[i]="教养"+table[i]
        elif i>=146 and i<163:
            table[i] = "控制" + str(table[i])
        elif i>=163 and i<176:
            table[i] = "领悟" + str(table[i])
        elif i>=176 and i<239:
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
    基本信息 [0:12]
    父母教养方式:[12:144]
    自我控制量表:[147:163]
    领悟社会支持:[164:176]
    应对方式问卷:[177:239]
    """
    # 2.数据清洗
    data=wash_process(data)  #
    # print(data)


    #共几个小维度
    n=0
    # 3.计算维度得分
    # 父母教养方式**************************************************************************
    father_factor1=(np.array([2,4,6,7,9,15,20,25,29,30,31,32,33,37,42,54,60,61,66])-1)*2+12
    mother_factor1=(np.array([2,4,6,7,9,15,25,29,30,31,32,33,37,42,44,54,60,61,63])-1)*2+13
    father_factor2=(np.array([1,10,11,14,27,36,48,50,56,57])-1)*2+12
    mother_factor2=(np.array([1,11,12,14,16,19,24,27,35,36,41,48,50,56,57,59])-1)*2+13
    father_factor3=(np.array([21,23,28,34,35,45])-1)*2+12
    mother_factor3=(np.array([23,26,28,34,38,39,45,47])-1)*2+13
    father_factor4=(np.array([5,13,17,18,43,49,51,52,53,55,58,62])-1)*2+12
    mother_factor4=(np.array([13,17,43,51,52,53,55,58,62])-1)*2+13
    father_factor5=(np.array([3,8,22,64,65])-1)*2+12
    mother_factor5=(np.array([3,8,22,64,65])-1)*2+13
    father_factor6 = (np.array([3, 8, 22, 64, 65]) - 1) * 2 + 12
    father_factor_all = np.concatenate((father_factor1,father_factor2,father_factor3,father_factor4,
                                        father_factor5,father_factor6,mother_factor1,mother_factor2,
                                        mother_factor3,mother_factor4,mother_factor5), axis=0)
    # print(data["14637李芸"][177:239])
    # 记分求和  父母教养方式
    title=np.array(["家庭教养方式:父亲情感温暖与理解关心","家庭教养方式:母亲情感温暖与理解关心",
           "家庭教养方式:父亲过分干涉","家庭教养方式:母亲过度干涉",
           "家庭教养方式:父亲拒绝与否认","家庭教养方式:母亲拒绝与否认",
           "家庭教养方式:父亲惩罚严厉","家庭教养方式:母亲惩罚严厉",
           "家庭教养方式:父亲偏爱被试","家庭教养方式:母亲偏爱被试",
           "家庭教养方式:父亲过度保护",
           "整体父母教养问题",
           ])
    n=n+len(title)
    data=sum_score(data,father_factor1,mother_factor1,father_factor2,mother_factor2,
              father_factor3,mother_factor3,father_factor4,mother_factor4,father_factor5,
              mother_factor5,father_factor6,father_factor_all)
    table=np.hstack((table,title))


    # 自我控制量表**************************************************************************
    reverse_order=np.array([2,3,9,12,15,16])+147-1
    data=p.reverce_score(data,reverse_order,6)
    control_factor1=np.array([1,10,5,14])+147-1
    control_factor2=np.array([4,13,15,16,6,11])+147-1
    control_factor3=np.array([2,12,3,7,8,9])+147-1
    control_factor_all=np.concatenate((control_factor1,control_factor2,control_factor3), axis=0)
    title2=np.array(["自我控制:冲动冒险","自我控制:情绪性","自我控制:简单倾向","整体自我控制能力差"])
    data=sum_score(data,control_factor1,control_factor2,control_factor3,control_factor_all)
    table = np.hstack((table, title2))
    n=n+len(title2)

    # 领悟社会支持**************************************************************************
    reverse_order=np.array([3,4,8,11,6,7,9,12,1,2,5,10])+164-1
    data = p.reverce_score(data, reverse_order,7)
    society_factory1=np.array([3,4,8,11])+164-1
    society_factory2=np.array([6,7,9,12])+164-1
    society_factory3=np.array([1,2,5,10])+164-1
    society_factory_all=np.concatenate((society_factory1,society_factory2,society_factory3), axis=0)
    title3 = np.array(["领悟社会支持:缺乏家庭支持", "领悟社会支持:缺乏朋友支持", "领悟社会支持:缺乏其他支持","个体整体的社会支持低"])
    data = sum_score(data, society_factory1, society_factory2, society_factory3,society_factory_all)

    table = np.hstack((table, title3))
    n=n+len(title3)

    # 应对方式问卷**************************************************************************
    reverse_order = np.array([1,2,3,5,8,19,29,31,40,46,51,55,10,11,14,36,39,48,50,56,57,59]) + 177 - 1
    data = p.reverce_score(data, reverse_order,1)
    process_factory1 = np.array([1,2,3,5,8,19,29,31,40,46,51,55]) + 177 - 1
    process_factory2 = np.array([15,23,25,37,48,50,56,57,59]) + 177 - 1
    process_factory3 = np.array([10,11,14,36,39,48,50,56,57,59]) + 177 - 1
    process_factory4 = np.array([4,12,17,21,22,26,28,41,45,49]) + 177 - 1
    process_factory5 = np.array([7,13,16,19,24,27,32,34,35,44,47]) + 177 - 1
    process_factory6 = np.array([6,9,18,20,30,33,38,52,54,58,61]) + 177 - 1
    title4 = np.array(["应对方式:不擅长解决问题","应对方式:自责","应对方式:不擅长求助","应对方式:幻想","应对方式:退避","应对方式:合理化"])
    data = sum_score(data, process_factory1, process_factory2, process_factory3,process_factory4,process_factory5,process_factory6)
    table = np.hstack((table, title4))
    n=n+len(title4)

    # 3.5打标签之前做一次统计,并存入表格,便于后续生成其他的数据
    # 生成统计意义上的{feature:均值,方差,min,max,基本信息:[基本信息集合],维度的标签阈值:[即大维度和小维度的得分阈值界限,超过即需要打标签]}
    table = process_empty(table)
    static_map = {}
    static_map = p.static(static_map, data, table, 0, 12, 12, 144)
    static_map["教养"]=[2]
    static_map = p.static(static_map, data, table, 146, 147, 147, 163)
    static_map["控制"] = [0]
    static_map = p.static(static_map, data, table, 163, 164, 164, 176)
    static_map["领悟"] = [0]
    static_map = p.static(static_map, data, table, 176, 177, 177, 239)
    static_map["应对"] = [2]
    # 返回static_map后,还差各个大小维度总和的阈值,在步骤4中添加

    # 4.打标签
    table=np.hstack((table, np.array(["标签"])))
    flag_map,static_map=cul_flag(data,table,n,0.27,static_map)
    print("共计算了{}个大小维度".format(n))
    # print("每个犯人的标签:",flag_map)


    #5.建表
    thieves_table_name=config.get_tablename("thieves_name")
    sql_createTb="create table {} (id int primary key auto_increment,data_type int(1) ,`{}`char(10) not null default '',"+"`{}` char(8) not null default '',"*(len(table)-2) +"{} text(1000))CHARSET=utf8;"
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
        sql_insert = "insert into {} values(default,0," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert=sql_insert.format(thieves_table_name,*adata,join(flag_map[key]))
        except:
            sql_insert=sql_insert.format(thieves_table_name,*adata,"无")
        print(sql_insert)
        con.insert(sql_insert)
    # print(table)
    # print(data)
    # print(len(table))

    # 7.保存table用于提供web接口
    np.save(curPath.mainPath()+"/thieves_dq/thieves.npy", table)
    # 3.5+4步骤中的数据static_map进行保存
    sava_to_json.save_json(static_map,curPath.mainPath()+"/temp_file/thieves_static_map")