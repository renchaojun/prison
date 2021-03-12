# -*- coding: utf-8 -*-
import os
from pathlib import Path
from utils2 import load_json, load_pickle, dump_json, dump_pickle, pwd, now,isfile
import logging
from sklearn.cluster import KMeans
from preprocess import cutwords
from reprs import worker
from density_peak import dp
from clusterer import DPClusterer, KMeansClusterer
import argparse
import random

output_dir = os.path.join(pwd(__file__), './output')
log_dir = os.path.join(pwd(__file__), './logs')

logfile = os.path.join(log_dir, 'clustering_{}.log'.format(now()))
logging.basicConfig(filename=logfile, level=logging.INFO)
defaultlogger = logging.getLogger("Democracy")

docs_file = os.path.join(pwd(__file__), './data/data.pkl')


def democracy(docs_reprs: list,all_doc:list,n_representers=15, cluster='kmeans',logger=defaultlogger):
    assert isinstance(docs_reprs, list)

    districts = []

    logger.info("Groups {}".format(len(docs_reprs)))
    clusterer=None

    if cluster == 'kmeans':
        logger.info("Kmeans clustering...")
        clusterer = KMeansClusterer()
    else:
        logger.info("DP clustering...")
        clusterer = DPClusterer()

    for group_idx, docs_repr in enumerate(docs_reprs):
        # labels must be {1,2,3,4}
        labels = clusterer.cluster(docs_repr)
        categories = list(set(labels))
        # labels must be {1,2,3,4}
        categories.sort()
        logger.info("{}th group has {} labels".format(
            group_idx, len(categories)))
        for category in categories:
            voters = []
            representers = None

            for offset, label in enumerate(labels):
                if int(label) == int(category):
                    voters.append(group_idx+offset*15)
            logger.info("Group {} category {} has {} voters".format(group_idx,category,len(voters)))
            if len(voters) < n_representers:
                representers = voters
                logger.info("Group {} category {} short of representers actual num {}".format(group_idx,category,len(voters)))
            else:
                representers = voters[:n_representers]

            districts.append({
                "voters": voters,
                "representers": representers
            })
        
       
    voters=[]
    for district in districts:
        voters.extend(district['voters'])
 

    logger.info("{} districts in total".format(len(districts)))

    return districts


if __name__ == "__main__":
    logger=defaultlogger
    datas = load_pickle(docs_file)
    docs = [w['note'] for w in datas]
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-c", help="clusterer:'kmeans' or 'dp'", type=str, default='kmeans')
    args = argparser.parse_args()


    if args.c not in ['kmeans', 'dp']:
        raise Exception("Illegal args")
    
    logger.info('{} democracy clustering'.format(args.c))
    

    docs_representes = []
    
    if isfile(os.path.join(output_dir,'{}_districts.json'.format(args.c))) and \
        isfile(os.path.join(output_dir,'{}_docsrepresenter.pkl'.format(args.c))):
        logger.info('Existing representer pkl loading...')
        docs_representes=load_pickle(os.path.join(output_dir,'{}_docsrepresenter.pkl'.format(args.c)))
        logger.info('Num of representers {}'.format(len(docs_representes)))

    else:
        logger.info('Loading docs from scratch...')
        docs_reprs = []
        count=0
        for idx in range(15):
            result = load_pickle(os.path.join(output_dir, "{}.pkl".format(idx)))
            docs_reprs.append(result)
            count+=len(result)
        #15个组分别聚类并选代表,生成vote选民和代表 的json
        districts = democracy(docs_reprs,docs,cluster=args.c,logger=defaultlogger)


        logger.info("Dumping districts.json")
        dump_json(os.path.join(output_dir, "{}_districts.json".format(args.c)), districts)

        for district in districts:
            for representer in district['representers']:
                docs_representes.append(docs[representer])
        logger.info("Num of representers {}".format(len(docs_representes)))
        dump_pickle(docs_representes,os.path.join(output_dir,"{}_docsrepresenter.pkl".format(args.c)))

    docs = cutwords(docs_representes)
    
    words=set()
    for doc in docs:
        words.update(doc)
    logger.info('Num words {}'.format(len(words)))
    worker(docs, '{}_representer'.format(args.c),logger=logger)
