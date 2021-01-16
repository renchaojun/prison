import utils.parse_config as u
import numpy as np
import utils.database as db
import utils.save_to_json as sava_to_json
import curPath
import copy
import time
import random
import datetime
import thieves_dq.read_thieve as th
import position_zw.position as p
import position_zw.random_generate as pr
"""
这部分根据统计信息thieves_static_map完成数据的随机生成,并写入数据库,虚拟数据的data_type=1
1.读取统计文件thieves_static_map.json
2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
3.计算总分,按照打标签static_map中最后一项阈值,完成打标签
4.构造sql,写入数据库
"""


def random_name(sex):
    # 删减部分，比较大众化姓氏
    firstName = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻水云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅卞齐康伍余元卜顾孟平" \
                "黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计成戴宋茅庞熊纪舒屈项祝董粱杜阮席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田胡凌霍万柯卢莫房缪干解应宗丁宣邓郁单杭洪包诸左石崔吉" \
                "龚程邢滑裴陆荣翁荀羊甄家封芮储靳邴松井富乌焦巴弓牧隗山谷车侯伊宁仇祖武符刘景詹束龙叶幸司韶黎乔苍双闻莘劳逄姬冉宰桂牛寿通边燕冀尚农温庄晏瞿茹习鱼容向古戈终居衡步都耿满弘国文东殴沃曾关红游盖益桓公晋楚闫"
    # 百家姓中双姓氏
    firstName2 = "万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁段干百里东郭南门呼延羊舌微生梁丘左丘东门西门南宫南宫"
    # 女孩名字
    girl = '秀娟英华慧巧美娜静淑惠珠翠雅芝玉萍红娥玲芬芳燕彩春菊兰凤洁梅琳素云莲真环雪荣爱妹霞香月莺媛艳瑞凡佳嘉琼勤珍贞莉桂娣叶璧璐娅琦晶妍茜秋珊莎锦黛青倩婷姣婉娴瑾颖露瑶怡婵雁蓓纨仪荷丹蓉眉君琴蕊薇菁梦岚苑婕馨瑗琰韵融园艺咏卿聪澜纯毓悦昭冰爽琬茗羽希宁欣飘育滢馥筠柔竹霭凝晓欢霄枫芸菲寒伊亚宜可姬舒影荔枝思丽'
    # 男孩名字
    boy = '伟刚勇毅俊峰强军平保东文辉力明永健世广志义兴良海山仁波宁贵福生龙元全国胜学祥才发武新利清飞彬富顺信子杰涛昌成康星光天达安岩中茂进林有坚和彪博诚先敬震振壮会思群豪心邦承乐绍功松善厚庆磊民友裕河哲江超浩亮政谦亨奇固之轮翰朗伯宏言若鸣朋斌梁栋维启克伦翔旭鹏泽晨辰士以建家致树炎德行时泰盛雄琛钧冠策腾楠榕风航弘'
    # 名
    name = '中笑贝凯歌易仁器义礼智信友上都卡被好无九加电金马钰玉忠孝'
    # 1%的机遇生成双数姓氏
    if random.choice(range(100)) > 1:
        firstName_name = firstName[random.choice(range(len(firstName)))]
    else:
        i = random.choice(range(len(firstName2)))
        firstName_name = firstName2[i:i + 2]

    name_1 = ""
    # 生成并返回一个名字
    if sex == 0:
        girl_name = girl[random.choice(range(len(girl)))]
        if random.choice(range(2)) > 0:
            name_1 = name[random.choice(range(len(name)))]
        return firstName_name + name_1 + girl_name
    else:
        boy_name = boy[random.choice(range(len(boy)))]
        if random.choice(range(2)) > 0:
            name_1 = name[random.choice(range(len(name)))]
        return firstName_name + name_1 + boy_name
def cul_flag(data, table,n,arr):
    flag_map={}
    for key in data:
        dim=data[key].tolist()[-n:]     #后面的维度项目总分
        table2=table.tolist()[-n-1:-1]   #后面的维度项目标签
        flag_map[key]=[]
        for i in range(len(dim)):
            if dim[i]>arr[i]:
                flag_map[key].append(table2[i])
    return flag_map

if __name__ == '__main__':
    # 生成1k条虚拟数据
    N=1100
    # 1.读取统计文件position_static_map.json
    static_map = sava_to_json.load_json(curPath.mainPath() + "/temp_file/thieves_static_map")
    # print(len(static_map))

    # 2.根据文件生成基本数据,根据文件的均值和标准差按照正太分布生成随机的问卷分数
    data={}
    for i in range(N):
        #编号
        id=20000+i
        sex = random.choice(range(2)) #1表示男,0表示女
        name=random_name(sex)
        start_id=str(id)+name
        data[start_id] = []
        data[start_id].append(start_id)
        #性别 sex
        data[start_id].append(sex)
        # 添加问卷量表数据
        for key in static_map:
            if key!="boundary_score":
                if key=="编号" or key=="性别：男=1，女=0":
                    continue
                if len(static_map[key])>4:
                    #说明是基本信息,要随机抽
                    data[start_id].append(random.choice(static_map[key]))
                elif len(static_map[key])==4:
                    #说明是数据
                    data[start_id].append(pr.random_normal(static_map,key))
                elif len(static_map[key])==1:
                    num=static_map[key]
                    for i in range(num[0]):
                        data[start_id].append(None)
                else:
                    print("static_map生成错误,请检查代码")
                    exit()


    # 3.计算总分, 按照打标签static_map中最后一项阈值, 完成打标
    n=0
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
    n=n+12
    data=th.sum_score(data,father_factor1,mother_factor1,father_factor2,mother_factor2,
              father_factor3,mother_factor3,father_factor4,mother_factor4,father_factor5,
              mother_factor5,father_factor6,father_factor_all)

    # 自我控制量表**************************************************************************
    reverse_order = np.array([2, 3, 9, 12, 15, 16]) + 147 - 1
    data = p.reverce_score(data, reverse_order, 6)
    control_factor1 = np.array([1, 10, 5, 14]) + 147 - 1
    control_factor2 = np.array([4, 13, 15, 16, 6, 11]) + 147 - 1
    control_factor3 = np.array([2, 12, 3, 7, 8, 9]) + 147 - 1
    control_factor_all = np.concatenate((control_factor1, control_factor2, control_factor3), axis=0)
    data = th.sum_score(data, control_factor1, control_factor2, control_factor3, control_factor_all)
    n = n + 4
    # 领悟社会支持**************************************************************************
    reverse_order = np.array([3, 4, 8, 11, 6, 7, 9, 12, 1, 2, 5, 10]) + 164 - 1
    data = p.reverce_score(data, reverse_order, 6)
    society_factory1 = np.array([3, 4, 8, 11]) + 164 - 1
    society_factory2 = np.array([6, 7, 9, 12]) + 164 - 1
    society_factory3 = np.array([1, 2, 5, 10]) + 164 - 1
    society_factory_all = np.concatenate((society_factory1, society_factory2, society_factory3), axis=0)
    data = th.sum_score(data, society_factory1, society_factory2, society_factory3, society_factory_all)
    n = n + 4

    # 应对方式问卷**************************************************************************
    reverse_order = np.array(
        [1, 2, 3, 5, 8, 19, 29, 31, 40, 46, 51, 55, 10, 11, 14, 36, 39, 48, 50, 56, 57, 59]) + 177 - 1
    data = p.reverce_score(data, reverse_order,1)
    process_factory1 = np.array([1, 2, 3, 5, 8, 19, 29, 31, 40, 46, 51, 55]) + 177 - 1
    process_factory2 = np.array([15, 23, 25, 37, 48, 50, 56, 57, 59]) + 177 - 1
    process_factory3 = np.array([10, 11, 14, 36, 39, 48, 50, 56, 57, 59]) + 177 - 1
    process_factory4 = np.array([4, 12, 17, 21, 22, 26, 28, 41, 45, 49]) + 177 - 1
    process_factory5 = np.array([7, 13, 16, 19, 24, 27, 32, 34, 35, 44, 47]) + 177 - 1
    process_factory6 = np.array([6, 9, 18, 20, 30, 33, 38, 52, 54, 58, 61]) + 177 - 1
    data = th.sum_score(data, process_factory1, process_factory2, process_factory3, process_factory4, process_factory5,
                     process_factory6)
    n = n + 6

#---------------------------生成数据并求维度的和完毕-------------------------------------------
    # 根据阈值计算标签
    table=np.load(curPath.mainPath() + "/thieves_dq/thieves.npy",allow_pickle=True)
    flag_map=cul_flag(data,table,n,static_map["boundary_score"])

    # 4.数据写入
    config = u.ReadConfig()
    thieves_table_name = config.get_tablename("thieves_name")
    con = db.DB()
    for key in data:
        adata=data[key]
        sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
        try:
            sql_insert=sql_insert.format(thieves_table_name,*adata,th.join(flag_map[key]))
        except:
            sql_insert=sql_insert.format(thieves_table_name,*adata,"无")
        print(sql_insert)
        con.insert(sql_insert)