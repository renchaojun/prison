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
log_dir=os.path.join(pwd(__file__),'./logs')
logging.basicConfig(filename=os.path.join(
    pwd(__file__), './logs/{}.log'.format(now())), level=logging.INFO)
defaultlogger = logging.getLogger("GLSA Repr")

# input size must be large enough, use padding
class AutoEncoder(nn.Module):
    def __init__(self,input_size,hidden_size):
        super(AutoEncoder,self).__init__()
        self.input_size=input_size
        self.hidden_size=hidden_size
        self.i2h=nn.Linear(input_size,hidden_size)
        self.h2o=nn.Linear(hidden_size,input_size)
    
    def forward(self,input_x):
        hidden=self.i2h(input_x)
        hidden=F.sigmoid(hidden)
        output=self.h2o(hidden)
        return output,hidden


def train_autoencoder(autocoder:AutoEncoder,rawx):
    pass


class BertWordEmbedding:
    '''
     pretrained bert word embedding with cache built in.
    '''

    def __init__(self):
        logging.warning(
            "Make sure you have setup Bert server with all default settings")
        self.cache = {}
        self.size = 0
        self.bc = BertClient()

    def query(self, words):
        '''

        :param words: a list of words, or just a single word
        :return: a list of embeddings with element numpy ndarray or just an embedding for a single word,
        '''
        if isinstance(words, list):
            return [self._query_word(word) for word in words]
        else:
            return self._query_word(words)

    def __call__(self, words):
        return self.query(words)

    def _query_word(self, word):
        '''

        :param word: a word
        :return:  embedding for that word with dimension of 768
        '''
        word = word.strip()
        if word in self.cache:
            return self.cache[word]

        embedding = self.bc.encode([word])[0]
        self.cache[word] = embedding
        self.size = self.size + 1
        return embedding


class TSBert:
    def __init__(self):
        self.bert_db = BertWordEmbedding()

    def __call__(self, one, other):
        assert isinstance(one, str)
        assert isinstance(other, str)
        one_embedding = self.bert_db([one])

        other_embedding = self.bert_db([other])
        return 1 - scipy.spatial.distance.cosine(one_embedding, other_embedding)


def constructor_01(docs: list, words: list):
    if not isinstance(docs[0], list):
        # ie query doc
        return [1 if word in docs else 0 for word in words]

    word_doc_repr = [[0 for _ in range(len(docs))] for _ in range(len(words))]
    for word_idx, word in enumerate(words):
        for doc_idx, doc in enumerate(docs):
            if word in doc:
                word_doc_repr[word_idx][doc_idx] = 1
            else:
                word_doc_repr[word_idx][doc_idx] = 0
    return word_doc_repr


def docs_repr(docs: list,
              word_similarity_constructor=None,
              k_ratio=0.2,
              dim=1000,
              word_doc_repr_constructor=constructor_01,
              logger=defaultlogger
              ):
    if word_similarity_constructor is None:
        word_similarity_constructor = TSBert()
    logger.info('Start compute doc repr')
    vocab = set()
    for doc in docs:
        vocab.update(doc)
    vocab = list(vocab)

    S = np.asarray([[word_similarity_constructor(i, j)
                     for j in vocab] for i in vocab])

    logger.info('Num of words {}'.format(S.shape[0]))

    if len(vocab) >= dim:
        reduced_dim = dim
    else:
        reduced_dim = round(len(vocab) * k_ratio)
    logger.info("SVD reduced dim={}".format(reduced_dim))

    logger.info('Start reduce dimension')
    svd = TruncatedSVD(n_components=reduced_dim)
    svd.fit(S)

    word_doc = word_doc_repr_constructor(docs, vocab)
    doc_word = np.asarray(word_doc).transpose()

    densed_doc_word = svd.transform(doc_word)
    logger.info('Finish reduce dimension')

    return densed_doc_word
    #
    # word_doc = word_doc_repr_constructor(docs, vocab)
    # doc_word = np.asarray(word_doc).transpose()
    # return np.dot(doc_word,S)


def worker(docs, tag='',logger=defaultlogger):
    logger.info("{} started in process {}".format(tag,os.getpid()))
    bert = TSBert()

    pkl_filename = os.path.join(output_dir, "{}.pkl".format(tag))
    # if os.path.isfile(pkl_filename):
    #     logger.info("{} find pickle,skip".format(tag))
    #     return

    repr_ = docs_repr(docs, word_similarity_constructor=bert,logger=logger)
    print("生成向量的维度:",repr_.shape)
    logger.info("Dumping {}".format(tag))
    dump_pickle(repr_, pkl_filename)
    logger.info("Worker {} job done".format(tag))


def tfidf(docs,logger=defaultlogger):
    '''
     return a sparse tf idf representation
    '''
    logger.info("{} started in process {}".format("TF idf",os.getpid()))
    assert isinstance(docs,list)
    assert len(docs)>0
    assert isinstance(docs[0],list)
    assert isinstance(docs[0][0],str)
    pkl_filename=os.path.join(output_dir,"{}.pkl".format("tfidfrepr"))
    if os.path.isfile(pkl_filename):
        logger.info("{} find pickle skip... tfidf job done".format("tfidf"))
        return

    corpus=[
        ' '.join(doc) for doc in docs
    ]
    #sparse 0,1
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
 
 
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    assert len(docs)==tfidf.shape[0]
    logger.info("Dumping tfidf...")
    dump_pickle(tfidf,pkl_filename)
    logger.info("Dumping tfidf done")
    logger.info("TFIDF job done")

    return tfidf

def ldarepr(docs,logger=defaultlogger):
    pass
    




if __name__ == "__main__":


    logger=defaultlogger
    parser=argparse.ArgumentParser()
    parser.add_argument("-p",action='store_true')
    parser.add_argument("-s",type=int,default=600)
    parser.add_argument("-f",type=int,default=0)

    args=parser.parse_args()
   # some dirty work
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
   
    if args.p:
        logger.info("Multiple process mode")
    else:
        logger.info("Single process mode")

 
    data_pkl = os.path.join(pwd(__file__), './data/data.pkl')

    if os.path.isfile(data_pkl):
        logger.info("Exsiting pkl,loading...")
        datas = load_pickle(data_pkl)
    else:
        logger.info("Loading from json")
        loader = DataLoader()
        datas = loader()
        logger.info("Shuffle data")
        random.shuffle(datas)
        random.shuffle(datas)
        logger.info("Serialize data")
        dump_pickle(datas, data_pkl)

    logger.info("Loaded data {}".format(len(datas)))
    # data_per_worker = int(1e2)*6
    data_per_worker=int(args.s)
    num_worker = round(len(datas)/data_per_worker)

    logger.info("Data per worker={}, num worker={}".format(
        data_per_worker, num_worker))

    docs = [w['note'] for w in datas]
    ids = [w['qid'] for w in datas]
    docs=cutwords(docs)
    # worker(docs, "all") ##全部的进行向量化
    tasks=[[]for _ in range(num_worker)]

    #split work
    for idx,doc in enumerate(docs):
        tasks[idx%num_worker].append(doc)
    
    for idx,task in enumerate(tasks):
        logger.info("Task {} has {} docs".format(idx,len(task)))
    
    if args.p:
        with Pool(processes=3) as pool:
            logger.info("Starting assign tasks")
            for idx,task in enumerate(tasks[int(args.f):]):
                pool.apply_async(worker,(task,idx+int(args.f)))
            pool.close()
            pool.join()
    
        logger.info("Worker pool shutdown now")
    else:
        for idx,task in enumerate(tasks[int(args.f):]):
            worker(task,str(idx+int(args.f)))

    
