from utils2 import load_json, load_pickle, dump_json, dump_pickle, pwd, now,cosine_distance
import os
import logging
from clusterer import DPClusterer, KMeansClusterer
import numpy as np
from argparse import ArgumentParser
import numpy as np
from reprs import docs_repr
output_dir = os.path.join(pwd(__file__), './output')
# representer_file = os.path.join(output_dir, "representer.pkl")
districts_file = os.path.join(output_dir, './districts.json')
log_dir = os.path.join(pwd(__file__), './logs')

logfile = os.path.join(log_dir, 'clustering_{}.log'.format(now()))
logging.basicConfig(filename=logfile, level=logging.INFO)
logger = logging.getLogger("clustering")

docs_file = os.path.join(pwd(__file__), './data/data.pkl')

def find_districtidx(districts, idx):
    for district_idx, district in enumerate(districts):
        if idx in district['voters']:
            return district_idx
    raise Exception("Cannot find district!")

def find_label(labels,globalidx):
    for idx,label in labels:
        if idx==globalidx:
            return label
    raise Exception('Cannot find label')

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', type=str, default='kmeans',
                        help="Clustering method")
    

    args = parser.parse_args()

    if args.c not in ['kmeans', 'dp']:
        raise Exception('Illegal clustering method')
    

    if args.c=='kmeans':
        clusterer=KMeansClusterer()
    else:
        clusterer=DPClusterer()
    

    # 统计真实情况
    docs=load_pickle(docs_file)
    true_categories=set()
    for doc in docs:
        true_categories.add(doc['type'])
    print(true_categories)
    true_clusters=[]
    for category in true_categories:
        cluster=[]
        for globalidx,doc in enumerate(docs):
            if doc['type']==category:
                cluster.append(globalidx)

        true_clusters.append(cluster)   ###每个true_categorie真实的类别对应这个类别的[全部数据id列表]
    representer_file = os.path.join(
        output_dir, "{}_representer.pkl".format(args.c))
    districts_file = os.path.join(
        output_dir, '{}_districts.json'.format(args.c))

    districts = load_json(districts_file)
    logger.info("{} districts in total".format(len(districts)))
    results = list(range(1000*9))

    representers = []
    for district in districts:
        for representer in district['representers']:
            representers.append(representer)  #文件中所有区域选择出来的所有的代表们

    representer_result = load_pickle(representer_file)  #每个代表的向量

    labels =clusterer.cluster(representer_result)       #每个代表聚类后的类别0-9
    categories = list(set(labels))  #类别集合
    labels=list(zip(representers,labels)) #代表和聚类的结果:类别 的元祖


    # 统计街区的投票情况
    district_voting_results = [-1]*len(districts)   #[-1]*街区的数目

    for didx, district in enumerate(districts):  #第几didx个是第几个街区district
        #统计票数
        tickets = [0]*len(categories)  #九类
        for categoryidx , category in enumerate(categories):  #第几个位置是第几类
            for globalidx in district['representers']:
                if find_label(labels,globalidx)==category:
                    tickets[categoryidx]+=1
                  
        #选出最大的票数
        district_voting_results[didx] = categories[np.argmax(tickets)]

    for voteridx in range(1000*9):
        results[voteridx] = district_voting_results[find_districtidx(
            districts, voteridx)]
    clusters=[]
    # print(len(results))

    # 统计成分，最终的结果   每个category:[属于这个类别的id(0开始)]
    for category in categories:
        cluster=[]
        for globalidx,label in enumerate(results):
            if label==category:
                cluster.append(globalidx)
        
        clusters.append(cluster)

    map={}
    right=[]
    for cluster_idx,cluster in enumerate(clusters):
        statistic_results=[]
        for true_cluster in true_clusters:
            statistic_results.append(len(set(cluster).intersection(set(true_cluster))))
        print(statistic_results)
            
        right.append(max(statistic_results))
        print('Cluster {} belongs to {} true cluster'.format(cluster_idx,np.argmax(statistic_results)))
        map[cluster_idx]=np.argmax(statistic_results)
    print("聚类的整体准确率为:",sum(right)/9000)


   #########################增加的############################################

###每个split的任务的长度都不一样,所以每个组的向量不同
###但是总的合起来的类,降维后是相同的.



        

