import os

from csv_operation import read_to_dict, write_to_csv
from collections import defaultdict
import math
import random
import numpy as np


def get_origin_data(filename, vocabulary):
    labels = []
    news = []
    dicts = read_to_dict(filename)
    for single_dict in dicts.values():
        single_dict = eval(single_dict)
        for key, value in single_dict.items():
            value = list(value)
            for word in value:
                if word not in vocabulary:
                    value.remove(word)
            if len(value)!=0:
                news.append(value)
                labels.append(int(key))
    return news, labels


def create_vocabulary(filename, standard):
    vocabularies = read_to_dict(filename)
    vocabulary = []
    for word, message in vocabularies.items():
        message = eval(message)
        if (message['positive'] + message['negative']) >= standard:
            vocabulary.append(word)
    return vocabulary


def mutual_info(m, n, p, q):
    return n * 1.0 / m * math.log(m, (n+1)*1.0/(p*q))/ math.log(2)

def construct_dict():
    return [0]*2

def genFeature(datasets, labels, filename):
    fw = open(filename, 'w')
    word_feature = defaultdict(construct_dict)
    label_feature = [0]*2
    print("===========Extracting features.....=============")
    for i in range(len(datasets)):
        label = int(labels[i])
        dataset = datasets[i]
        for word in dataset:
            word_feature[word][label] += 1
            label_feature[label] += 1
    print("========Calculating mutual information=========")
    mDict = defaultdict(construct_dict)
    N = sum(label_feature)
    for k, vs in word_feature.items():
        for i in range(len(vs)):
            N11 = vs[i]
            N10 = sum(vs) - N11
            N01 = label_feature[i] - N11
            N00 = N - N11 - N10 - N01
            mi = mutual_info(N, N11, N10+N11, N01+N11) + mutual_info(N, N10, N10+N11, N00+N10) + mutual_info(N,N01,N01+N11,N01+N00)+ mutual_info(N,N00,N00+N10,N00+N01)
            mDict[k][i] = mi
    fWords = set()
    for i in range(len(label_feature)):
        keyf = lambda x:x[1][i]
        sortedDict = sorted(mDict.items(), key=keyf, reverse=True)
        for j in range(len(sortedDict)):
            fWords.add(sortedDict[j][0])
            fw.write(sortedDict[j][0]+',')
    return fWords, label_feature


#------------Generate training features-----------
    # standard: create vocabulary with words occurred more than standard times

def __preparation_bayes(standard):
    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
    vocabulary = create_vocabulary(datapath+"/word_message.csv", standard)
    posts_list, classes_list = get_origin_data(datapath+"/origin_news_data.csv", vocabulary)
    fWords, label_feature = genFeature(posts_list, classes_list, datapath+"/features.csv")
