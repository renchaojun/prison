#coding=utf-8
# aiohttpdemo_polls/main.py
from aiohttp import web
from web.settings import config
import utils.database as db
import numpy as np
import curPath
import utils.save_to_json as s
# 请求格式
# http://localhost:8080/prisoners/main?CODE=6415004248   原来的是这样
# 新的格式
# http://localhost:8080/prisoners/type=thieves&code=?
# http://localhost:8080/prisoners/type=position&code=?
# http://localhost:8080/prisoners/type=fraudsters&code=?


def process(type,code):
    con = db.DB()
    sql="select * from {} where id={}".format(type,code)
    data=con.select(sql)
    res = {}
    if len(data)==1:
        # 查询到一个
        adata=data[0]
        # 导出table
        if type=="thieves":
            table=np.load(curPath.mainPath()+"/thieves_dq/thieves.npy",allow_pickle=True)
        elif type=="position":
            table=np.load(curPath.mainPath()+"/position_zw/position.npy",allow_pickle=True)
        elif type=="fraudsters":
            table=np.load(curPath.mainPath()+"/fraudsters_zp/fraudsters.npy",allow_pickle=True)
        elif type=="drug":
            table=np.load(curPath.mainPath()+"/drug/drug.npy",allow_pickle=True)
        elif type == "traffic":
            table = np.load(curPath.mainPath() + "/traffic/traffic.npy", allow_pickle=True)
        elif type == "rape":
            table = np.load(curPath.mainPath() + "/violence/rape.npy", allow_pickle=True)
        elif type=="rob":
            table=np.load(curPath.mainPath()+"/violence/rob.npy",allow_pickle=True)
        elif type=="damage":
            table=np.load(curPath.mainPath()+"/violence/damage.npy",allow_pickle=True)
        elif type == "intentkill":
            table = np.load(curPath.mainPath() + "/violence/intentkill.npy", allow_pickle=True)
        else:
            return {"err":"参数错误!"}
        assert len(table)==len(adata)-2
        table=np.hstack((np.array(["id","data_type"]),table))
        for i in range(len(table)):
            res[table[i]]=adata[i]
        return res
    elif len(data)==0:
        res["status"]="id is not found!"
        return res
    return res
class Handler:

    def __init__(self):
        pass

    async def handle_intro(self, request):
        return web.Response(text="Hello, guys")
    async def handle_plan(self, request):
        txt={}
        flag = request.match_info.get('flag')
        print(flag)
        if flag in flag_method.keys():
            txt["flag"]=flag
            methods=flag_method[flag]
            for m in methods:
                txt[m]=method_plan[m]
        else:
            txt["status"] = "flag is not found!"
        return web.json_response(txt)

    async def handle_greeting(self, request):
        type = request.match_info.get('type')
        code = request.match_info.get('code')
        assert type in table
        txt=process(type,code)
        # print(txt)
        return web.json_response(txt)

handler = Handler()
app = web.Application()
table=["thieves","position","fraudsters","drug","traffic","rape","rob","damage","intentkill"]
flag_method=s.load_json(curPath.mainPath() + "/temp_file/flag_method.json")
print(flag_method.keys())
method_plan=s.load_json(curPath.mainPath() + "/temp_file/method_plan.json")
app.add_routes([web.get('/prisoners', handler.handle_intro),
                web.get('/prisoners/flag={flag}', handler.handle_plan),
                web.get('/prisoners/type={type}&code={code}', handler.handle_greeting)])
# print(config)
app['config'] = config
web.run_app(app)