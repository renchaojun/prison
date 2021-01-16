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
处理暴力犯:
1.数据读
2.数据清洗(不需要数据清洗,因为没有缺失值)
3.计算总分
4.打标签  
5.新建数据库
6.数据写入
"""
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
        if  j>=4:
            lie=arr[:,j]
            sum=0
            num=0
            for i in range(len(lie)):
                # if type(lie[i])==int:
                if type(lie[i])==int:
                    num=num+1
                    sum=sum+int(lie[i])
            ave=round(sum/num)
            for i in range(len(lie)):
                if type(lie[i])!=int :
                    arr[i][j]=ave  #替换完成
    # 把arr的数据放入data
    for line in arr:
        data[line[0]]=line
    return data
def sum_score(data,*items,score):
    """这部分是来计算不是正常加求和的情况,值为
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
                if int(float(adata[j]))==score:
                    sum+=1
            inner_arr.append(sum)
        data[adata[0]]=np.hstack((data[adata[0]],np.array(inner_arr)))

    #处理inner_arr 进行评估是否含有这个标签
    return data
def sum_score_div(data,item_1,item_2):
    """
    :param data: map
    :param items: tuple
    :return:
    """
    for key in data:
        inner_arr=[] #一个犯人的得分
        adata=data[key]
        sum=0
        sum2=0
        for j in item_1:
            sum+=int(adata[j])
        for j in item_2:
            sum2+=int(adata[j])
        if sum2>=3:
            sum+=1
        data[adata[0]]=np.hstack((data[adata[0]],np.array(sum)))
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
        if j==24: # 效度,阈值设置的比较大,不打标签
            basic_score.append(1000)
            continue
        if j==18:  #儿童期虐待已经有阈值
            basic_score.append(15)
            continue
        elif j==19:
            basic_score.append(13)
            continue
        elif j==20:
            basic_score.append(10)
            continue
        elif j==21:
            basic_score.append(8)
            continue
        elif j==22:
            basic_score.append(10)
            continue
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
def wash_three(data,j):
    """
    把生成的数据按照效度洗一遍,j是效度所在的列
    :param data:
    :param j:
    :return:
    """

    n_data={}
    for key in data:
        if data[key][j]!=3:
            n_data[key]=data[key]
    return n_data
if __name__ == '__main__':
    file_name = "violence_file"
    config = u.ReadConfig()
    table, data = d.read_position_excel(config, file_name)  # 得到全部的列数据和表头

    # print(data)

    # 2.清洗数据(忽略)
    data=wash_process(data)

    # 3.计算总分
    n = 0

    """
    反社会人格障碍:
        八个大题目,>=3分即反社会人格障碍
        第八个题目,>=3分则记1分
    """

    antisocial_=np.array(range(1,8))+4-1
    antisocial_8=np.array(range(8,23))+4-1  #>=3   则为1
    title = np.array(["反社会人格障碍"])
    data = sum_score_div(data,antisocial_,antisocial_8)
    table=np.hstack((table,title))
    n = n + len(title)

    """
        精神病态
    """

    reverse_order = np.array([5,11,14,17,21,22,25])+26-1
    data = p.reverce_score(data, reverse_order, 4)
    Mental_illness1=np.array([1,4,6,7,9,10,11,12,13,14,15,17,19,20,22,24])+26-1
    Mental_illness2=np.array([2,3,5,8,16,18,21,23,25,26])+26-1
    title2=["原发性精神病态","继发性精神病态"]
    data = p.sum_score(data, Mental_illness1,Mental_illness2)
    table = np.hstack((table, title2))
    n = n + len(title2)

    """
    冲动性/预谋性攻击
    """
    reverse_order = np.array([4,7]) + 52- 1
    data = p.reverce_score(data, reverse_order, 5)
    attack1 = np.array([3,4,6,7,8,16,17,18]) + 52 - 1
    attack2 = np.array([1,2,5,9,10,11,12,13,14,15,19,20]) + 52- 1
    title3 = ["冲动性攻击", "预谋性攻击"]
    data = p.sum_score(data, attack1, attack2)
    table = np.hstack((table, title3))
    n = n + len(title3)
    """
    父母教养方式:
        1,4,7,12,14,19
        2,6,9,11,13,17,21
        3,5,8,10,15,16,18,20
    """
    reverse_order = np.array([15]) + 72- 1
    data = p.reverce_score(data, reverse_order, 4)
    breeding1=np.array([1,2,7,8,13,14,23,24,27,28,37,39,]) + 72 - 1
    breeding2=np.array([3,4,11,12,17,18,21,22,25,26,33,34,41,42,]) + 72 - 1
    breeding3=np.array([5,6,9,10,15,16,19,20,29,30,31,32,35,36,39,40,]) + 72 - 1
    breeding_all=np.concatenate((breeding1,breeding2,breeding3), axis=0)
    title4 = ["父母教养方式:拒绝维度", "父母教养方式:情感温暖","父母教养方式:过度保护","父母教养方式不适"]
    data = p.sum_score(data, breeding1, breeding2,breeding3,breeding_all)
    table = np.hstack((table, title4))
    n = n + len(title4)
    """
    道德推脱:
        道德辩护：18、22、24、29；
        委婉标签：12、14、17、32；
        有利比较：4、21、23、27；
        责任转移：1、5、20、26；
        责任分散：6、13、16、30；
        扭曲结果：7、9、11、25；
        责备归因：3、10、15、19；
        非人性化：2、8、28、31。
    """
    moral1=np.array([18,22,24,29]) + 114 - 1
    moral2=np.array([12,14,17,32]) + 114 - 1
    moral3=np.array([4,21,23,27]) + 114 - 1
    moral4=np.array([1,5,20,26]) + 114 - 1
    moral5=np.array([6,13,16,30]) + 114 - 1
    moral6=np.array([7,9,11,25]) + 114 - 1
    moral7=np.array([3,10,15,19]) + 114 - 1
    moral8=np.array([2,8,28,31]) + 114 - 1
    moral_all=np.concatenate((moral1,moral2,moral3,moral4,moral5,moral6,moral7,moral8), axis=0)
    title5 = ["道德推脱:道德辩护", "道德推脱:委婉标签","道德推脱:有利比较","道德推脱:责任转移",
              "道德推脱:责任分散","道德推脱:扭曲结果","道德推脱:责备归因","道德推脱:非人性化",
              "道德推脱",]
    data = p.sum_score(data, moral1, moral2,moral3,moral4,moral5,moral6,moral7,moral8,moral_all)
    table = np.hstack((table, title5))
    n = n + len(title5)
    """
    儿童期虐待:
        情感忽视:5,7,13,19,28    15
        情感虐待:3,8,14,18,25     13 
        躯体虐待:9,11,12,15,17    10
        性虐待:20,21,23,24,27     8
        躯体忽视:1,2,4,6,26       10
    """
    reverse_order = np.array([5,7,13,19,28,1,2,4,6,26]) + 146 - 1
    data = p.reverce_score(data, reverse_order, 5)
    factor1=np.array([5,7,13,19,28]) + 146 - 1
    factor2=np.array([3,8,14,18,25]) + 146 - 1
    factor3=np.array([9,11,12,15,17]) + 146 - 1
    factor4=np.array([20,21,23,24,27]) + 146 - 1
    factor5=np.array([1,2,4,6,26]) + 146 - 1
    factor_all=np.concatenate((factor1,factor2,factor3,factor4,factor5), axis=0)
    effect=np.array([10,16,22])+146-1  #：选5记1分，选非5记0分,如果3个效度条目总分为3分，剔除该问卷
    title6 = ["儿童期虐待:情感忽视", "儿童期虐待:情感虐待", "儿童期虐待:躯体虐待","儿童期虐待:性虐待",
              "儿童期虐待:躯体忽视","儿童遭受期虐待水平高","效度"]
    data = p.sum_score(data, factor1, factor2, factor3, factor4, factor5, factor_all)
    data = sum_score(data, effect,score=5)
    table = np.hstack((table, title6))
    n = n + len(title6)
    """
    犯罪态度和同伴:
        暴力态度:1，2，3，4，5，6，7，8，9，10，12，13
        情绪权利:11，14，15，16，17，18，19，21，32，34，37，38
        反社会意图:20，22，23，24，25，26，27，28，29，30，31，36
        同伴态度:33，35，39，40，41，42，43，44，45，46
        个体持有的犯罪态度强
    """
    reverse_order = np.array([25,28,31,35,39,41,45]) + 174 - 1
    data = p.reverce_score(data, reverse_order, 5)
    attitude1=np.array([1,2,3,4,5,6,7,8,9,10,12,13]) + 174 - 1
    attitude2=np.array([11,14,15,16,17,18,19,21,32,34,37,38]) + 174 - 1
    attitude3=np.array([20,22,23,24,25,26,27,28,29,30,31,36]) + 174 - 1
    attitude4=np.array([33,35,39,40,41,42,43,44,45,46]) + 174 - 1
    attitude_all=np.concatenate((attitude1,attitude2,attitude3,attitude4), axis=0)
    data = p.sum_score(data, attitude1, attitude2, attitude3, attitude4,attitude_all)
    title7 = ["犯罪态度和同伴:暴力态度","犯罪态度和同伴:情绪权利","犯罪态度和同伴:反社会意图",
              "犯罪态度和同伴:同伴态度","个体持有的犯罪态度强"]
    table = np.hstack((table, title7))
    n = n + len(title7)
    #********************分开讨论不同的犯罪类型*********************************************#
    # 强奸:rape   抢劫:rob  故意伤害:damage  故意杀人:kill

    # 再次清洗,效度==3,删除数据
    data=wash_three(data,244)

    # 3.5打标签之前做一次统计,并存入表格,便于后续生成其他的数据
    # 生成统计意义上的{feature:均值,方差,min,max,基本信息:[基本信息集合],维度的标签阈值:[即大维度和小维度的得分阈值界限,超过即需要打标签]}
    # 数据分开
    data_rape={}
    data_rob={}
    data_damage={}
    data_kill={}
    for key in data:
        if data[key][3]=="强奸罪":
            data_rape[key]=data[key]
        elif data[key][3]=="抢劫":
            data_rob[key]=data[key]
        elif data[key][3]=="故意伤害":
            data_damage[key]=data[key]
        elif data[key][3]=="故意杀人":
            data_kill[key]=data[key]
        else:
            print("该数据没有犯罪类型")
    table = np.hstack((table, np.array(["标签"])))
    #分开统计
    all_data=[data_rape,data_rob,data_damage,data_kill]
    tablename = ["rape", "rob", "damage", "intentkill"]
    for i in range(len(all_data)):
        n_data=all_data[i]  #第几类人员 :强奸罪....
        static_map = {}
        static_map =p.static(static_map, n_data, table, 0, 4, 4,220)
        # 返回static_map后,还差各个大小维度总和的阈值,在步骤4中添加

        # 4.打标签
        flag_map, static_map = cul_flag(n_data, table, n, 0.27, static_map)
        # print("共计算了{}个大小维度".format(n))

        # 5.建表
        position_table_name = config.get_tablename(tablename[i]+"_name")
        sql_createTb = "create table {} (id int primary key auto_increment,data_type int(1) ,`{}`char(20) not null default ''," + "`{}` char(30) not null default ''," * (
                    len(table) - 2) + "{} text(1000))Engine=MyISAM CHARSET=utf8;"
        sql_createTb = sql_createTb.format(position_table_name, *table)
        # print(table)
        print(sql_createTb)
        con = db.DB()
        con.chech_table_exit(position_table_name, sql_createTb)

        # 6.数据写入
        data_arr = []
        # print(len(table))
        # print(flag_map)
        for key in n_data:
            adata = n_data[key]
            sql_insert = "insert into {} values(default,0," + "'{}'," * (len(adata)) + "'{}');"
            try:
                sql_insert = sql_insert.format(position_table_name, *adata, p.join(flag_map[key]))
            except:
                sql_insert = sql_insert.format(position_table_name, *adata, "无")
            print(sql_insert)
            con.insert(sql_insert)

        # 7.保存table用于提供web接口:   如: data_rape.npy
        np.save(curPath.mainPath() + "/violence/{}.npy".format(tablename[i]), table)
        # 3.5+4步骤中的数据static_map进行保存  data_rape_static_map
        sava_to_json.save_json(static_map, curPath.mainPath() + "/temp_file/{}_static_map".format(tablename[i]))

