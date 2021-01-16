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
"""
这部分根据统计信息position_static_map完成数据的随机生成,并写入数据库,虚拟数据的data_type=1
1.读取统计文件position_static_map.json
2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
3.计算总分,按照打标签static_map中最后一项阈值,完成打标签
4.构造sql,写入数据库
"""


def random_name():
    # 删减部分，比较大众化姓氏
    firstName = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻水云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅卞齐康伍余元卜顾孟平" \
                "黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计成戴宋茅庞熊纪舒屈项祝董粱杜阮席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田胡凌霍万柯卢莫房缪干解应宗丁宣邓郁单杭洪包诸左石崔吉" \
                "龚程邢滑裴陆荣翁荀羊甄家封芮储靳邴松井富乌焦巴弓牧隗山谷车侯伊宁仇祖武符刘景詹束龙叶幸司韶黎乔苍双闻莘劳逄姬冉宰桂牛寿通边燕冀尚农温庄晏瞿茹习鱼容向古戈终居衡步都耿满弘国文东殴沃曾关红游盖益桓公晋楚闫"
    # 百家姓中双姓氏
    firstName2 = "万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁段干百里东郭南门呼延羊舌微生梁丘左丘东门西门南宫南宫"
    # 男孩名字
    boy = '伟刚勇毅俊峰强军平保东文辉力明永健世广志义兴良海山仁波宁贵福生龙元全国胜学祥才发武新利清飞彬富顺信子杰涛昌成康星光天达安岩中茂进林有坚和彪博诚先敬震振壮会思群豪心邦承乐绍功松善厚庆磊民友裕河哲江超浩亮政谦亨奇固之轮翰朗伯宏言若鸣朋斌梁栋维启克伦翔旭鹏泽晨辰士以建家致树炎德行时泰盛雄琛钧冠策腾楠榕风航弘'
    # 名
    name = '中笑贝凯歌易仁器义礼智信友上都卡被好无九加电金马钰玉忠孝'
    # 3%的机遇生成双数姓氏
    if random.choice(range(100)) > 2:
        firstName_name = firstName[random.choice(range(len(firstName)))]
    else:
        i = random.choice(range(len(firstName2)))
        firstName_name = firstName2[i:i + 2]
    name_1 = ""
    boy_name = boy[random.choice(range(len(boy)))]
    if random.choice(range(2)) > 0:
        name_1 = name[random.choice(range(len(name)))]
    return firstName_name + name_1 + boy_name
def randomtimes(start, end, frmt="%Y-%m-%d-%H-%M"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    return random.random() * (etime - stime) + stime
def random_normal(static_map,key):
    tem=static_map[key]
    a=round(np.random.normal(tem[0],tem[1],1)[0])
    if a<tem[2]:
        a=tem[2]
    elif a>tem[3]:
        a=tem[3]
    return a
def cul_flag(data, table,n,arr):
    flag_map={}
    for key in data:
        dim=data[key].tolist()[-n:]     #后面的维度项目总分
        table2=table.tolist()[-n-1:-1]   #后面的维度项目标签
        flag_map[key]=[]
        for i in range(len(dim)):
            if float(dim[i])>float(arr[i]):
                flag_map[key].append(table2[i])
    return flag_map

if __name__ == '__main__':
    # 生成1k条虚拟数据
    N=1100
    # 1.读取统计文件position_static_map.json
    static_map=sava_to_json.load_json(curPath.mainPath()+"/temp_file/position_static_map")
    print(len(static_map))

    # 2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    data={}
    for i in range(N):
        my_id=static_map["自编号"][-1]+1+i
        name=random_name()
        prison_room=random.choice(static_map["监狱"])
        prison_area=random.choice(static_map["监区"])
        r_id=4500000000+i
        birth=randomtimes('1956-01-01-0-0','1985-12-30-0-0')
        birth2=birth.strftime("%Y-%m-%d %H:%M:%S")
        survey_data=randomtimes('2019-01-01-0-0','2020-12-30-0-0').strftime("%Y-%m-%d %H:%M:%S")
        criminal_type=random.choice(static_map["罪名"])
        age=2021-birth.year
        sentence=random.choice(static_map["刑期"])
        Residual_period=random.choice(static_map["余刑"])
        education=random.choice(static_map["受教育程度"])
        birth_area=random.choice(static_map["出生所在地"])
        hukou_area=random.choice(static_map["目前户口所在地"])
        money=random.choice(static_map["家庭经济状况（14岁前）"])
        position=random.choice(static_map["服刑前行政职务"])
        position_class=random.choice(static_map["服刑前行政职级"])
        position_class2=random.choice(static_map["行政职级（根据职务）"])
        position_class3=random.choice(static_map["服刑前所在单位"])
        father_edu=random.choice(static_map["父亲受教育程度"])
        mother_edu=random.choice(static_map["母亲受教育程度"])
        father_position=random.choice(static_map["父亲职业"])
        mother_position=random.choice(static_map["母亲职业"])
        marry=random.choice(static_map["婚姻状况"])
        number_sun=random.choice(static_map["子女数量"])
        foregn_situaction=random.choice(static_map["子女出国情况"])
        about_money=random.choice(static_map["涉案金额（万元）"])
        time=random.choice(static_map["首次涉嫌职务犯罪距离参加工作的时间"])
        time2=random.choice(static_map["首次涉嫌职务犯罪距离被发现的时间"])
        why=random.choice(static_map["案发原因"])
        why2=random.choice(static_map["案发原因其他备注"])


        data[my_id]=[]
        data[my_id]=data[my_id]+[my_id,name,prison_room,prison_area,r_id,
                                 birth2,survey_data,
                                 criminal_type,age,sentence,Residual_period,education,
                                 birth_area,hukou_area,money,position,position_class,
                                 position_class2,position_class3,father_edu,mother_edu,father_position,
                                 mother_position,marry,number_sun,foregn_situaction, about_money,
                                 time,time2,why,why2,
                                 ]
        # 添加问卷量表数据
        for key in static_map:
            if len(static_map[key])==4:
                temp=random_normal(static_map,key)
                data[my_id] = data[my_id] +[temp]
    n=0
    # 3.计算总分, 按照打标签static_map中最后一项阈值, 完成打标签
    """
        短式黑暗三联征:
    """

    reverse_order = np.array([11, 16, 20, 24, 26]) + 31 - 1
    data = p.reverce_score(data, reverse_order,5)

    three_feature_factor1 = (np.array(range(1, 10))) + 31 - 1
    three_feature_factor2 = (np.array(range(10, 19))) + 31 - 1
    three_feature_factor3 = (np.array(range(19, 28))) + 31 - 1
    three_feature_factor_all = np.concatenate((three_feature_factor1, three_feature_factor2, three_feature_factor3),
                                              axis=0)
    # 记分求和  短式黑暗三联征
    n = n + 4
    data = p.sum_score(data, three_feature_factor1, three_feature_factor2, three_feature_factor3,
                     three_feature_factor_all)

    # 责任性量表**************************************************************************
    reverse_order = np.array([1, 2, 4, 5, 7, 8, 10, 12]) + 58 - 1
    data = p.reverce_score(data, reverse_order,5)
    responsibility_factor1 = np.array(range(28, 40)) +31 - 1
    data = p.sum_score(data, responsibility_factor1)
    n = n + 1

    # # 心理特权感量表**************************************************************************
    reverse_order = np.array([5]) + 70 - 1
    data = p.reverce_score(data, reverse_order,7)
    psychological_factory1 = np.array(range(1, 10)) + 70 - 1
    data = p.sum_score(data, psychological_factory1)
    n = n + 1

    ## 物质主义价值观**************************************************************************
    reverse_order = np.array([2, 3, 5, 6, 10]) + 79 - 1
    data = p.reverce_score(data, reverse_order,5)
    money_factory1 = np.array([1, 3, 4, 6, 8]) + 79 - 1
    money_factory2 = np.array([2, 5, 9, 11, 13]) + 79 - 1
    money_factory3 = np.array([7, 10, 12]) + 79 - 1
    money_factory_all = np.concatenate((money_factory1, money_factory2, money_factory3), axis=0)
    data = p.sum_score(data, money_factory1, money_factory2, money_factory3, money_factory_all)
    n = n + 4

    # 道德推脱**************************************************************************
    moral_factory1 = np.array([18, 22, 24, 29]) + 92 - 1
    moral_factory2 = np.array([12, 14, 17, 32]) + 92 - 1
    moral_factory3 = np.array([4, 21, 23, 27]) + 92 - 1
    moral_factory4 = np.array([1, 5, 20, 26]) + 92 - 1
    moral_factory5 = np.array([6, 13, 16, 30]) + 92 - 1
    moral_factory6 = np.array([7, 9, 11, 25]) + 92 - 1
    moral_factory7 = np.array([3, 10, 15, 19]) + 92 - 1
    moral_factory8 = np.array([2, 8, 28, 31]) + 92 - 1
    moral_factory_all = np.concatenate((moral_factory1, moral_factory2, moral_factory3, moral_factory4,
                                        moral_factory5, moral_factory6, moral_factory7, moral_factory8), axis=0)

    data = p.sum_score(data, moral_factory1, moral_factory2, moral_factory3, moral_factory4, moral_factory5,
                     moral_factory6, moral_factory7, moral_factory8, moral_factory_all)

    n = n + 9
    #---------------------------生成数据并求维度的和完毕-------------------------------------------
    # 根据阈值计算标签
    table=np.load(curPath.mainPath() + "/position_zw/position.npy")
    flag_map=cul_flag(data,table,n,static_map["boundary_score"])

    # 4.数据写入
    config = u.ReadConfig()
    position_table_name = config.get_tablename("position_name")
    con = db.DB()
    for key in data:
        adata = data[key]
        # print(len(adata))
        # print(len(table))
        sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert = sql_insert.format(position_table_name, *adata,p.join(flag_map[key]))
        except:
            sql_insert = sql_insert.format(position_table_name, *adata, "无")
        print(sql_insert)
        con.insert(sql_insert)
