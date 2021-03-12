#这部分是预测新的一条数据属于哪个类别的
#预测前需要先把pre_new_data.pkl删除
import os
from pathlib import Path
from utils2 import load_json, load_pickle, dump_json, dump_pickle, pwd, now
import logging
from preprocess import cutwords
from reprs import worker
from density_peak import dp
import nltk
from nltk.cluster.kmeans import KMeansClusterer as KM
from utils2 import cosine_distance
from bert_serving.client import BertClient
import logging
import scipy.spatial
from utils2 import pwd, now, load_json, load_pickle, dump_json, dump_pickle
import os
import numpy as np
from sklearn.decomposition import TruncatedSVD
from preprocess import DataLoader, cutwords
import random
from multiprocessing import Pool,TimeoutError
import argparse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import torch
import torch.nn as nn
import torch.nn.functional as F
from preprocess import cutwords
output_dir = os.path.join(pwd(__file__), './output')
if __name__ == '__main__':
    N=100  #每个类别有100个文本参与比较
    type=['fraudsters', 'intentkill', 'thieves', 'rape', 'traffic', 'rob', 'position', 'drug', 'damage']
    num=[N for _ in range(9)]
    data_pkl = os.path.join(pwd(__file__), './data/data.pkl')
    datas = load_pickle(data_pkl)
    documents = []   #存放的比较的文档
    for i,atype in enumerate(type):
        for apeople in datas:
            if apeople["type"]==atype and num[i]>0:
                documents.append(apeople["note"])
                num[i]=num[i]-1
                if num[i]==0:
                    break
    print("用于对比的文本规模:",len(documents))

    # adata="乔元,56岁,游手好闲,抢劫他人手机,犯抢劫罪"        ##需要预测的数据
    adata="14216黄明英,29岁,家庭教养方式不足,加入盗窃团伙,实施盗窃"       ##需要预测的数据
    documents.append(adata)
    # print(documents)
    docs = cutwords(documents)
    worker(docs, "pre_new_data")
    repsimenter_vector=load_pickle(os.path.join(output_dir,"{}.pkl".format("pre_new_data")))
    sim=[]  #保存待比较的案例和库里面的相似度 N*9个数据,并统计最可能出现的概率
    for repr_vector in repsimenter_vector[0:-1]:
        sim.append(cosine_distance(repr_vector,repsimenter_vector[-1]))
    sim=np.reshape(np.array(sim),[-1,N])
    res=[]
    for i in range(9):
        res.append(sum(sim[i])/len(sim[i]))
        
    print("预测该类属于:",type[res.index(min(res))])

