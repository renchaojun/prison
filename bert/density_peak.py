# DP Algorithm
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import collections
import matplotlib.pyplot as plt
import pickle
import pathlib
from scipy import spatial
import os
from pathlib import Path
import argparse
import pickle
import logging
from pathlib import Path
from scipy import spatial
from utils2 import cosine_distance



def euclidean_distance(x1, x2):
    return np.linalg.norm(x1 - x2) ** 2


# 用欧式距离计算样本集的距离矩阵
# 参数：样本集x，类型为np.array
def get_distance(x, distance_func=None):
    if distance_func is None:
        distance_func = cosine_distance

    size = len(x)
    distance = np.zeros(shape=(len(x), len(x)))
    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dij = distance_func(x[i], x[j])
           
            distance[i][j] = dij
            distance[j][i] = distance[i][j]
    return distance


# 选择最优的截断距离dc
# 参数：距离矩阵distance，平均近邻百分比t（t=2表示平均每个样本的近邻样本数为样本总数的2%）
def choose_dc(distance, t):
    temp = []
    for i in range(len(distance[0])):
        for j in range(i + 1, len(distance[0])):
            temp.append(distance[i][j])
    temp.sort()
    dc = temp[int(len(temp) * t / 100)]
    return dc


# 通过Cut-off kernel方法计算局部密度列表
# 参数：距离矩阵distance，截断距离dc
def get_discrete_density(distance, dc):
    density = np.zeros(shape=len(distance))
    for index, node in enumerate(distance):
        density[index] = len(node[node < dc])
    return density


# 通过Gaussian kernel方法计算局部密度
# Gaussian kernel方法：np.sum(np.exp(-(dist / dc) ** 2))
# 参数：距离矩阵distance，截断距离dc
def get_continous_density(distance, dc):
    density = np.zeros(shape=len(distance))
    for index, dist in enumerate(distance):
        density[index] = np.sum(np.exp(-(dist / dc) ** 2))
    return density


# 计算NN距离列表，找到聚类中心列表
# 参数：密度列表density，距离矩阵distance
def get_dist_center(density, distance):
    dist = np.zeros(shape=len(distance))  # 距离列表
    closest_leader = np.zeros(shape=len(distance), dtype=np.int32)  # 聚类中心列表
    for index, node in enumerate(distance):
        # 局部密度更大的样本列表
        larger_density = np.squeeze(np.argwhere(density > density[index]))
        # 如果存在局部密度更大的样本
        if larger_density.size != 0:
            # 局部密度更大样本与当前样本的距离列表
            larger_distance = distance[index][larger_density]
            # 当前样本的距离为larger_distance中的最小值
            dist[index] = np.min(larger_distance)
            # 局部密度更大样本中与当前样本距离相等（最小值可能有多个）的样本集
            min_distance_sample = np.squeeze(np.argwhere(larger_distance == dist[index]))
            # 有多个局部密度更大且距离当前样本最近的样本时，选择第一个样本作为聚类中心
            if min_distance_sample.size >= 2:
                min_distance_sample = np.random.choice(a=min_distance_sample)
            if larger_distance.size > 1:
                closest_leader[index] = larger_density[min_distance_sample]
            else:
                closest_leader[index] = larger_density
        # 如果没有局部密度更大的样本（当前样本局部密度最大）
        else:
            dist[index] = np.max(distance)
            closest_leader[index] = index
    return dist, closest_leader


# 画原始数据分布图
# 参数：样本数据集x
def draw_x(x):
    for j in range(len(x)):
        plt.scatter(x=x[j, 0], y=x[j, 1], marker='o', c='k', s=8)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Sample data')
    plt.show()


# 画密度-距离图
# 参数：局部密度列表density，距离列表dist，样本集x
def draw_density_dist(density, dist, x):
    plt.figure(num=1, figsize=(15, 9))
    for i in range(len(x)):
        plt.scatter(x=density[i], y=dist[i], c='k', marker='o', s=15)
    plt.xlabel('Density')
    plt.ylabel('Distance')
    plt.title('Decision graph')
    plt.show()


# 计算得分：局部密度与距离的乘积，并画出得分排序图
# 参数：局部密度列表density，距离列表dist
def get_score(density, dist):
    # 分别对局部密度和距离做归一化处理
    normal_density = (density - np.min(density)) / (np.max(density) - np.min(density))
    normal_distance = (dist - np.min(dist)) / (np.max(dist) - np.min(dist))
    # 计算得分
    score = normal_density * normal_distance
    # 画出决策图
    plt.figure(num=2, figsize=(15, 10))
    plt.scatter(x=range(len(dist)), y=-np.sort(-score), c='k', marker='o', s=-np.sort(-score) * 100)
    plt.xlabel('n')
    plt.ylabel('score')
    plt.title('Rank Score')
    plt.show()
    return score


# 完成聚类
# 参数：聚类中心cluster_centers，
def clustering(cluster_centers, chose_list):
    for i in range(len(cluster_centers)):
        while cluster_centers[i] not in chose_list:
            j = cluster_centers[i]
            cluster_centers[i] = cluster_centers[j]
    C = cluster_centers[:]
    return C  # C[i]表示第i点所属最终分类


# 画聚类结果
# 参数：聚类簇C，样本集x，聚类中心centers
def draw_cluster(C, x, centers):
    colors = ['b', 'r', 'c', 'm', 'g', 'y', 'k', 'w', 'gold', 'pink', 'orange', 'purple']
    center_color = {}
    final = dict(collections.Counter(C)).keys()
    for index, i in enumerate(final):
        center_color[i] = index
    # 画最终聚类图
    plt.figure(num=3, figsize=(15, 10))
    for i, categorie in enumerate(C):
        if i in centers:  # 标出各个聚类簇的中心
            plt.scatter(x=x[i, 0], y=x[i, 1], marker='s', s=100, c='K', alpha=0.8)
        else:
            plt.scatter(x=x[i, 0], y=x[i, 1], c=colors[center_color[categorie]], s=5, marker='h',
                        alpha=0.66)
    plt.title('Cluster Result')
    plt.show()


# dp聚类算法
# 参数：样本数据集X
def dp(X):
    t = 1.1  # 样本集大小的百分比：1.1%
    distance = get_distance(X)  # 样本的距离矩阵
    dc = choose_dc(distance, t)  # 最优截断距离dc（根据t）
    density = get_continous_density(distance, dc)  # 局部密度列表
    dist, cluster_center = get_dist_center(density, distance)  # 得到距离列表和聚类中心列表
    # draw_x(X)  # 画样本数据分布图
    # draw_density_dist(density, dist, X)  # 画密度-距离图
    scores = get_score(density, dist)  # 计算局部密度与距离的乘积，并画出得分排序图
    # cluster_num = int(input('Input clusters num: '))  # 看图决定最终的聚类簇数目
    cluster_num=3
    centers = np.argsort(-scores)[: cluster_num]  # 得分最高的前cluster_num个作为最终聚类中心
    C = clustering(cluster_center, centers)  # 完成所有点的聚类
    # draw_cluster(C, X, centers)
    return C  # 画出聚类结果图










