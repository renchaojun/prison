import os
from pathlib import Path
from utils2 import load_json, load_pickle, dump_json, dump_pickle, pwd, now
import logging
from sklearn.cluster import KMeans
from preprocess import cutwords
from reprs import worker
from density_peak import dp
import nltk
from nltk.cluster.kmeans import KMeansClusterer as KM
from utils2 import cosine_distance

class Clusterer:
    def cluster(self, docs_repr):
        raise NotImplementedError


class KMeansClusterer(Clusterer):
    def __init__(self, n_clusters=9):
        self.n_clusters=n_clusters

    def cluster(self, docs_repr):
        kclusterer = KM(self.n_clusters, distance=cosine_distance, repeats=25,avoid_empty_clusters=True)
        assigned_clusters = kclusterer.cluster(docs_repr, assign_clusters=True)
        return assigned_clusters


        # model=KMeans(n_clusters=self.n_clusters,max_iter=500)
        # model.fit(docs_repr)
        # return model.labels_


class DPClusterer(Clusterer):
    def cluster(self, docs_repr):
        result=dp(docs_repr)
        return result

                    