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
import violence.read_excel as v

if __name__ == '__main__':
    N=1100
    # N=1
    tablename = ["rape", "rob", "damage", "intentkill"]
    for j in range(len(tablename)):
        data={}
        static_map = sava_to_json.load_json(curPath.mainPath() + "/temp_file/{}_static_map".format(tablename[j]))
        for i in range(N):
            name=pr.random_name()
            data[name]=[]
            data[name].append(name)
            birth=pr.randomtimes('1956-01-01-0-0','1985-12-30-0-0')
            age = 2021 - birth.year
            birth2 = birth.strftime("%Y-%m-%d")
            data[name].append(birth2)
            data[name].append(age)
            data[name].append(random.choice(static_map["组别"]))
            # 添加问卷量表数据
            for key in static_map:
                if len(static_map[key])==4:
                    temp = pr.random_normal(static_map, key)
                    data[name] = data[name] + [temp]

        # 3.计算总分
        n = 0
        """
        反社会人格障碍:
            八个大题目,>=3分即反社会人格障碍
            第八个题目,>=3分则记1分
        """
        antisocial_ = np.array(range(1, 8)) + 4 - 1
        antisocial_8 = np.array(range(8, 23)) + 4 - 1  # >=3   则为1
        data = v.sum_score_div(data, antisocial_, antisocial_8)
        n = n + 1

        """
            精神病态
        """

        reverse_order = np.array([5, 11, 14, 17, 21, 22, 25]) + 26 - 1
        data = p.reverce_score(data, reverse_order, 4)
        Mental_illness1 = np.array([1, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 24]) + 26 - 1
        Mental_illness2 = np.array([2, 3, 5, 8, 16, 18, 21, 23, 25, 26]) + 26 - 1
        data = p.sum_score(data, Mental_illness1, Mental_illness2)
        n = n + 2

        """
        冲动性/预谋性攻击
        """
        reverse_order = np.array([4, 7]) + 52 - 1
        data = p.reverce_score(data, reverse_order, 5)
        attack1 = np.array([3, 4, 6, 7, 8, 16, 17, 18]) + 52 - 1
        attack2 = np.array([1, 2, 5, 9, 10, 11, 12, 13, 14, 15, 19, 20]) + 52 - 1

        data = p.sum_score(data, attack1, attack2)
        n = n +2
        """
        父母教养方式
        """
        reverse_order = np.array([15]) + 72 - 1
        data = p.reverce_score(data, reverse_order, 4)
        breeding1 = np.array([1, 4, 7, 12, 14, 19]) + 72 - 1
        breeding2 = np.array([2, 6, 9, 11, 13, 17, 21]) + 72 - 1
        breeding3 = np.array([3, 5, 8, 10, 15, 16, 18, 20]) + 72 - 1
        breeding_all = np.concatenate((breeding1, breeding2, breeding3), axis=0)
        data = p.sum_score(data, breeding1, breeding2, breeding3, breeding_all)
        n = n + 4
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
        moral1 = np.array([18, 22, 24, 29]) + 114 - 1
        moral2 = np.array([12, 14, 17, 32]) + 114 - 1
        moral3 = np.array([4, 21, 23, 27]) + 114 - 1
        moral4 = np.array([1, 5, 20, 26]) + 114 - 1
        moral5 = np.array([6, 13, 16, 30]) + 114 - 1
        moral6 = np.array([7, 9, 11, 25]) + 114 - 1
        moral7 = np.array([3, 10, 15, 19]) + 114 - 1
        moral8 = np.array([2, 8, 28, 31]) + 114 - 1
        moral_all = np.concatenate((moral1, moral2, moral3, moral4, moral5, moral6, moral7, moral8), axis=0)
        data = p.sum_score(data, moral1, moral2, moral3, moral4, moral5, moral6, moral7, moral8, moral_all)
        n = n +9
        """
        儿童期虐待:
            情感忽视:5,7,13,19,28    15
            情感虐待:3,8,14,18,25     13 
            躯体虐待:9,11,12,15,17    10
            性虐待:20,21,23,24,27     8
            躯体忽视:1,2,4,6,26       10
        """
        reverse_order = np.array([5, 7, 13, 19, 28, 1, 2, 4, 6, 26]) + 146 - 1
        data = p.reverce_score(data, reverse_order, 5)
        factor1 = np.array([5, 7, 13, 19, 28]) + 146 - 1
        factor2 = np.array([3, 8, 14, 18, 25]) + 146 - 1
        factor3 = np.array([9, 11, 12, 15, 17]) + 146 - 1
        factor4 = np.array([20, 21, 23, 24, 27]) + 146 - 1
        factor5 = np.array([1, 2, 4, 6, 26]) + 146 - 1
        factor_all = np.concatenate((factor1, factor2, factor3, factor4, factor5), axis=0)
        effect = np.array([10, 16, 22]) + 146 - 1  # ：选5记1分，选非5记0分,如果3个效度条目总分为3分，剔除该问卷

        data = p.sum_score(data, factor1, factor2, factor3, factor4, factor5, factor_all)
        data = v.sum_score(data, effect, score=5)
        n = n + 7
        # 再次清洗,效度==3,删除数据
        data = v.wash_three(data, 244)
        """
        犯罪态度和同伴:
            暴力态度:1，2，3，4，5，6，7，8，9，10，12，13
            情绪权利:11，14，15，16，17，18，19，21，32，34，37，38
            反社会意图:20，22，23，24，25，26，27，28，29，30，31，36
            同伴态度:33，35，39，40，41，42，43，44，45，46
            个体持有的犯罪态度强
        """
        reverse_order = np.array([25, 28, 31, 35, 39, 41, 45]) + 174 - 1
        data = p.reverce_score(data, reverse_order, 5)
        attitude1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13]) + 174 - 1
        attitude2 = np.array([11, 14, 15, 16, 17, 18, 19, 21, 32, 34, 37, 38]) + 174 - 1
        attitude3 = np.array([20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 36]) + 174 - 1
        attitude4 = np.array([33, 35, 39, 40, 41, 42, 43, 44, 45, 46]) + 174 - 1
        attitude_all = np.concatenate((attitude1, attitude2, attitude3, attitude4), axis=0)
        data = p.sum_score(data, attitude1, attitude2, attitude3, attitude4, attitude_all)
        n = n + 5

        # ---------------------------生成数据并求维度的和完毕-------------------------------------------
        # 根据阈值计算标签
        table = np.load(curPath.mainPath() + "/violence/{}.npy".format(tablename[j]))
        flag_map = pr.cul_flag(data, table, n, static_map["boundary_score"])

        # 4.数据写入
        config = u.ReadConfig()
        table_name = config.get_tablename(tablename[j]+"_name")
        con = db.DB()
        for key in data:
            adata = data[key]
            sql_insert = "insert into {} values(default,1," + "'{}'," * (len(adata)) + "'{}');"
            if len(flag_map[key])!=0:
                sql_insert = sql_insert.format(table_name, *adata, p.join(flag_map[key]))
            else:
                sql_insert = sql_insert.format(table_name, *adata, "无")

            print(sql_insert)
            con.insert(sql_insert)
