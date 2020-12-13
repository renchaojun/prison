# aiohttpdemo_polls/main.py
from aiohttp import web
from web.settings import config
import utils.database as db
import numpy as np
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
    # 查询到一个
    adata=data[0]
    # 导出table
    if type=="thieves":
        table=np.load("../thieves_dq/thieves.npy",allow_pickle=True)
        print(table)
    elif type=="position":
        table=np.load("../position_zw/position.npy",allow_pickle=True)
    elif type=="fraudsters":
        table=np.load("../fraudsters_zp/fraudsters.npy",allow_pickle=True)
    else:
        return {"err":"参数错误!"}
    res={}
    assert len(table)==len(adata)-1
    res["id"]=code
    for i in range(len(table)):
        res[table[i]]=adata[i+1]
    return res

class Handler:

    def __init__(self):
        pass

    async def handle_intro(self, request):
        return web.Response(text="Hello, world")

    async def handle_greeting(self, request):
        type = request.match_info.get('type', "Anonymous")
        code = request.match_info.get('code', "Anonymous")
        assert type in table
        txt=process(type,code)
        print(txt)
        return web.json_response(txt)

handler = Handler()
app = web.Application()
table=["thieves","position","fraudsters"]

app.add_routes([web.get('/prisoners', handler.handle_intro),
                web.get('/prisoners/type={type}&code={code}', handler.handle_greeting)])
# print(config)
app['config'] = config
web.run_app(app)