#encoding=utf-8
import numpy as np
import utils.save_to_json as s
import curPath
if __name__ == '__main__':
    """
    诈骗: '恶意创造力','马氏+自恋'
    职务: "短式黑暗三联征:马基雅维利主义","短式黑暗三联征:精神病态","短式黑暗三联征:自恋","整体具有某种黑暗特质","责任感差","心理特权感水平高",
            "物质主义价值观:以财物定义成功","物质主义价值观:以获取财物为中心","物质主义价值观:通过获取财物追求幸福","物质主义整体水平高",
            "道德推脱:道德辩护", "道德推脱:委婉标签", "道德推脱:有利比较","道德推脱:责任转移", "道德推脱:责任分散", "道德推脱:扭曲结果",
            "道德推脱:责备归因", "道德推脱:非人性化","整体道德推脱的水平高",
    盗窃: "家庭教养方式:父亲情感温暖与理解关心","家庭教养方式:母亲情感温暖与理解关心",
           "家庭教养方式:父亲过分干涉","家庭教养方式:母亲过度干涉",
           "家庭教养方式:父亲拒绝与否认","家庭教养方式:母亲拒绝与否认",
           "家庭教养方式:父亲惩罚严厉","家庭教养方式:母亲惩罚严厉",
           "家庭教养方式:父亲偏爱被试","家庭教养方式:母亲偏爱被试",
           "家庭教养方式:父亲过度保护",
           "整体父母教养问题",
           "自我控制:冲动冒险","自我控制:情绪性","自我控制:简单倾向","整体自我控制能力差"
           "领悟社会支持:缺乏家庭支持", "领悟社会支持:缺乏朋友支持", "领悟社会支持:缺乏其他支持","个体整体的社会支持低"
           "应对方式:不擅长解决问题","应对方式:自责","应对方式:不擅长求助","应对方式:幻想","应对方式:退避","应对方式:合理化"
    交通肇事: "安全驾驶态度:妨碍道路畅通且不规则遵守","安全驾驶态度:超速驾驶","安全驾驶态度:激情驾驶","整体安全驾驶态度差"
            "驾驶员自我效能感差",
            "个体越容易把交通事故归结为其他驾驶员原因",
              "个体越容易把交通事故归结为自身原因",
              "个体越容易把交通事故归结为车辆和环境原因",
              "个体越容易把交通事故归结为命运原因",
              "个体越容易把交通事故归结为某一因素"
              "责任性差"
    暴力犯: "反社会人格障碍","原发性精神病态","继发性精神病态","冲动性攻击", "预谋性攻击"
          "父母教养方式:拒绝维度", "父母教养方式:情感温暖","父母教养方式:过度保护","父母教养方式不适",
          "儿童期虐待:情感忽视", "儿童期虐待:情感虐待", "儿童期虐待:躯体虐待","儿童期虐待:性虐待",
              "儿童期虐待:躯体忽视","儿童遭受期虐待水平高",
           "道德推脱:道德辩护", "道德推脱:委婉标签","道德推脱:有利比较","道德推脱:责任转移",
            "道德推脱:责任分散","道德推脱:扭曲结果","道德推脱:责备归因","道德推脱:非人性化",
            "道德推脱",
          "犯罪态度和同伴:暴力态度","犯罪态度和同伴:情绪权利","犯罪态度和同伴:反社会意图",
          "犯罪态度和同伴:同伴态度","个体持有的犯罪态度强"
    """
    flag_method={
        "冲动性":["认知行为疗法(01)","正念干预疗法(02)","TMS(03)"],
        "社会支持":["家庭治疗方法(04)", "内观疗法(05)"],
        "应对方式":["团体绘画疗法(06)", "认知行为疗法(07)","团体沙盘游戏(08)"],
        "非理性认知":["认知行为疗法(09)"],
        "恶意创造力":["虚拟疗法(10)"],
        "马氏+自恋":["虚拟疗法(11)"],
        "短式黑暗三联征":["虚拟疗法(12)"],
        "物质主义价值观":["虚拟疗法(13)"],
        "心理特权感":["虚拟疗法(14)"],
        "责任感":["虚拟疗法(15)"],
        "道德推脱":["虚拟疗法(16)"],
        "家庭教养":["虚拟疗法(17)"],
        "自我控制":["虚拟疗法(18)"],
        "安全驾驶态度":["虚拟疗法(19)"],
        "反社会人格障碍":["虚拟疗法(20)"],
        "精神病态":["虚拟疗法(21)"],
        "攻击":["虚拟疗法(22)"],
        "儿童遭受期虐待":["虚拟疗法(23)"],
        "犯罪态度和同伴":["虚拟疗法(24)"],
        }
    method_plan={
           "认知行为疗法(01)":{
               "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"①年龄20-69岁，身体健康，文化程度为初中及以上，同意并遵守团体要求，包括足够的认知理解水平。\n②冲动性：Barratt冲动性量表筛选前27%，同时结合他评、自评结果。",
                "单元":["单元1(00001)", "单元2(00002)"]},
            "正念干预疗法(02)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00003)", "单元2(00004)"]},
            "TMS(03)": {
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00005)", "单元2(00006)"]},
            "家庭治疗方法(04)":{
                "age":"20-69岁",
                "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00007)", "单元2(00008)"]},
            "内观疗法(05)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00009)", "单元2(00010)"]},
            "团体绘画疗法(06)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00011)", "单元2(00012)"]},
            "认知行为疗法(07)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00013)", "单元2(00014)"]},
            "团体沙盘游戏(08)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00015)", "单元2(00016)"]},
            "认知行为疗法(09)":{
                "age":"20-69岁",
               "edu":"初中及以上",
                "适用人群":"暂时没有",
                "单元":["单元1(00017)", "单元2(00018)"]},
            "虚拟疗法(10)": {
                "age": "暂时没有",
                "edu": "暂时没有",
                "适用人群": "暂时没有",
                "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
            "虚拟疗法(11)": {
                "age": "暂时没有",
                "edu": "暂时没有",
                "适用人群": "暂时没有",
                "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(12)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(13)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(14)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(15)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(16)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(17)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(18)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(19)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(20)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(21)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(22)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(23)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},
        "虚拟疗法(24)": {
            "age": "暂时没有",
            "edu": "暂时没有",
            "适用人群": "暂时没有",
            "单元": ["虚拟单元1(00017)", "虚拟单元2(00018)"]},

        }
    s.save_json(flag_method,curPath.mainPath()+"/temp_file/flag_method.json")
    s.save_json(method_plan,curPath.mainPath()+"/temp_file/method_plan.json")