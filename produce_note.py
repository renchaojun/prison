import utils.parse_config as u
import utils.database as db
import curPath
import utils.save_to_json as sava_to_json
import random
def save_to_txt(rate_his, file_path):
    with open(file_path, 'w') as f:
        for rate in rate_his:
            f.write("%s \n" % rate)
config = u.ReadConfig()

thieves=config.get_tablename("thieves_name")
fraudsters=config.get_tablename("fraudsters_name")
position=config.get_tablename("position_name")
drug=config.get_tablename("drug_name")
traffic=config.get_tablename("traffic_name")
rape=config.get_tablename("rape_name")
rob=config.get_tablename("rob_name")
damage=config.get_tablename("damage_name")
intentkill=config.get_tablename("intentkill_name")
tables=[thieves,fraudsters,position,drug,traffic,rape,rob,damage,intentkill]
print(tables)
con = db.DB()
data_json=[]
def position_note():
    a=["公职人员,","公务员,","某县县长","村长,","省委书记,","省长,","某市文化馆馆长,","烟草局局长,"]
    money=["50万元","100万元","2亿","2000万元","1000多万","500万","300万元","80万元","300多万","800万元","1200万元","1.5亿"]
    rea=["涉及金额{}".format(random.choice(money)),"贪污{}".format(random.choice(money)),"滥用公职,以权谋私,长期贪污腐败"]
    return random.choice(rea)
def drup_note(type):
    rea=[type,"因其家人从事贩毒,","因从事毒品的贩卖,","因长期从事毒品的贩卖","因长期吸毒,","因有很大毒瘾,","因长期购买并使用毒品,","因吸食毒品,","因长期吸食毒品,"]
    p="被捕入狱"
    return random.choice(rea)+p
def rape_note():
    tool=["单身,","离婚,","未婚,",]
    xing=["王","张","陈","赵","雷","孙","李","任",]
    thing=["将受害人{}某强奸,","将受害人{}某强奸,","强奸{}某,","强奸{}某某,","强奸未遂,"]
    a=["强吻,猥亵妇女,","强吻,猥亵{}某,","猥亵{}某某,",]
    type="犯强奸罪"
    return random.choice(tool)+random.choice(thing).format(random.choice(xing))+"还多次"+random.choice(a)+type
def rob_note():
    tool = ["无生活来源,","不务正业,","好吃懒做,","游手好闲,","",]
    thing=["手机","名贵手表","包包","现金","名贵首饰","项链","金首饰","金项链",]
    mod = ["持刀抢劫他人{},", "尾随并抢劫他人{},",""]
    type="犯抢劫罪"
    return random.choice(tool)+random.choice(mod).format(random.choice(thing))+type
def kill_note():
    tool=["自己的亲生母亲","他人","同学","朋友","同村人","老板","上司","同事","亲人"]
    mod=["拿刀砍死{}","拿刀将{}杀害","与{}发生争执,并将其杀害","将{}杀害","与{}发生冲突,于是杀人","将{}杀害,并将尸体藏匿","将{}勒死杀害"]
    return random.choice(mod).format(random.choice(tool))
def damege_note():
    tool=["具有精神病态,","具有一定精神病态","具有原发性精神病态,","具有继发性精神病态,"]
    mod="犯故意伤害罪"
    return random.choice(tool)+mod
def fraudsters_note():
    p=["电话","网络"]
    tool=["实施{}诈骗",]
    return "从事诈骗活动,"+random.choice(tool).format(random.choice(p))
def thieves_note():
    rea=["家庭教养方式不足,","父母教养方式存在问题,","缺乏父母管教,","母亲教养不足,","父亲教养不足,",]
    p=["加入盗窃团伙,实施盗窃","半夜潜入房间实施盗窃","长期从事偷窃,以盗窃为生","趁他人不备盗窃,犯盗窃罪",]
    return random.choice(rea)+random.choice(p)
if __name__ == '__main__':
    name_set=set()
    for i in range(len(tables)):
        table=tables[i]  # 确定表名
        # 查看这个表多少数据
        sql = "select * from {}".format(table)
        data=con.select(sql)
        print(len(data))
        con.add("alter table {} add  note text(50);".format(table)) #添加列
        if table=="thieves":
            qid_start=0

            #处理盗窃
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[2]
                age=adata[4]
                note=name+","+str(age)+"岁,"+thieves_note()
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"]=qid_start+int(id)
                adata_json["type"]=table
                adata_json["note"]=note
                data_json.append(adata_json)
                name_set.add(name)
        if table=="fraudsters":
            qid_start = 1000
            #处理诈骗表
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[4]
                age=adata[6]
                money=random.randint(10000,1000000)
                note=name+","+str(age)+"岁,"+fraudsters_note()
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table=="position":
            qid_start = 2000
            #处理职务犯
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[3]
                type=adata[9]
                age=adata[10]
                note="职务犯"+name+","+str(age)+"岁,"+type+position_note()
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table=="drug":
            qid_start = 3000
            #处理贩毒
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                age=adata[3]
                edu=adata[4]
                type=adata[5]
                note=str(age)+"岁,"+edu+"文化程度,"+drup_note(type)
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
        if table=="traffic":
            qid_start = 4000
            #处理交通肇事
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[2]
                note=name+","+"犯交通肇事逃逸罪,安全驾驶态度较差"
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table=="rape":
            qid_start = 5000
            #处理强奸
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[2]
                age = adata[4]
                note=name+","+str(age)+"岁,"+rape_note()
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table=="rob":
            qid_start = 6000
            #处理抢劫
            for j in range(1000):
                adata=data[j]
                id=adata[0]
                name=adata[2]
                age = adata[4]
                note=name+","+str(age)+"岁,"+rob_note()
                # print(desc)
                sql_updata="update {} set note=\"{}\" where id={};".format(table,note,int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table == "damage":
            qid_start = 7000
            # 故意伤害
            for j in range(1000):
                adata = data[j]
                id = adata[0]
                name = adata[2]
                age = adata[4]
                type = adata[7]
                note = name + "," + str(age) + "岁," +damege_note()
                # print(desc)
                sql_updata = "update {} set note=\"{}\" where id={};".format(table, note, int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        if table == "intentkill":
            qid_start = 8000
            # 故意杀人
            for j in range(1000):
                adata = data[j]
                id = adata[0]
                name = adata[2]
                age = adata[4]
                type = adata[7]
                note = name + "," + str(age) + "岁," + type+","+kill_note()
                # print(desc)
                sql_updata = "update {} set note=\"{}\" where id={};".format(table, note, int(id))
                # print(sql_updata)
                con.updata(sql_updata)

                adata_json = {}
                adata_json["qid"] = qid_start + int(id)
                adata_json["type"] = table
                adata_json["note"] = note
                data_json.append(adata_json)
                name_set.add(name)
        sava_to_json.save_json(data_json,curPath.mainPath()+"/bert/data/data.json")

        save_to_txt(name_set,curPath.mainPath()+"/bert/stopwords/姓名年龄岁.txt")  #bert里面进行用的时候,去掉这些姓名等词语,所以提前保存停止词