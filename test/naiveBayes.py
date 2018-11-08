import os
import sys
sys.path.append("..")
from base.csv_operation import *
import math
import random
from collections import defaultdict
import numpy as np


path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/train_data'
model_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/model'
father_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
test_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/test_data'


def generate_wordmessage(filename):
    dicts = read_to_dict(filename)
    words = {}
    for num, single_dict in dicts.items():
        single_dict = eval(single_dict)
        for key, value in single_dict.items():
            value = list(value)
            for word in value:
                if word not in words:
                    words[word] = 1
                else:
                    words[word] += 1
    write_to_csv(words, path+"/word_message.csv", ['word', 'times'])


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


def getTestNews(filename, vocabulary):
    labels = []
    news = []
    dicts = read_to_dict(filename)
    for single_dict in dicts.values():
        value = eval(single_dict)
        vt = list(value['title'])
        for word in vt:
            if word not in vocabulary:
                vt.remove(word)
        if len(vt)!=0:
            news.append(value)
            labels.append(int(value['flag']))
    return news, labels


def create_vocabulary(filename, standard):
    fw = open(filename, 'w')
    vocabularies = read_to_dict(filename)
    vocabulary = []
    for word, message in vocabularies.items():
        message = int(message)
        if message >= standard:
            vocabulary.append(word)
            fw.write(word+",")
    fw.close()
    return vocabulary


def mutual_info(m, n, p, q):
    return n * 1.0 / m * math.log(m, (n+1)*1.0/(p*q))/ math.log(2)

def construct_dict():
    return [0]*2

def genFeature(datasets, labels):
    word_feature = defaultdict(construct_dict)
    label_feature = [0]*2
    fw = open(path+"/feature.txt", 'w')
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
            fw.write(str(sortedDict[j][0])+ ',')
            fWords.add(sortedDict[j][0])
    fw.close()
    return fWords, label_feature


def train_bayes(fWords, trainsets, trainlabels, label_feature):
    wordCount = defaultdict(construct_dict)
    docCounts = label_feature
    tCount = [0]*len(docCounts)
    for i in range(len(trainsets)):
        label, text = trainlabels[i], trainsets[i]
        for word in text:
            if word in fWords:
                tCount[label] += 1
                wordCount[word][label] += 1
    print("=========Training finish===========")
    scores = {}
    for k,v in wordCount.items():
        score = [(v[i]+1) * 1.0 / (tCount[i]+len(wordCount)) for i in range(len(v))]
        scores[k] = score
    return scores


def predict_bayes(text,scores,fWords,label_feature):
    docCounts, features = label_feature, fWords
    docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
    print("==============Predicting===========")
    preValues = list(docScores)
    for word in text:
        if word in fWords:
            for i in range(len(preValues)):
                preValues[i] += math.log(scores[word][i])

    m = max(preValues)
    print("===========Predict Value========"+preValues.index(m)+"===========")
    return preValues.index(m)



def test_model(testSets, testLabels, scores, fWords, label_feature):
    docCounts, features = label_feature, fWords
    docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
    rCount = 0
    docCount = 0
    pCount = 0
    nCount = 0
    p = 0
    n = 0
    print("==============Testing=============")
    for j in range(len(testSets)):
        text = testSets[j]
        label = testLabels[j]
        preValues = list(docScores)
        for word in text:
            if word in scores.keys():
                for i in range(len(preValues)):
                    preValues[i] += math.log(scores[word][i])
        m = max(preValues)
        v = preValues.index(m)
        if int(v) == int(label):
            rCount += 1
        if int(label) == 1:
            p += 1
            if int(v) == 1: pCount += 1
        if int(label) == 0:
            n += 1
            if int(v) == 0: nCount += 1
        docCount += 1
    print("===========Testing Finish==========")
    print("Test Sample: %d" % docCount)
    print("Correct sample: %d" % rCount)
    print("Accuracy: %s" % str(rCount/docCount))
    print("Positive Accuracy: %s" % str(pCount/p))
    print("Negative Accuracy: %s" % str(nCount/n))


def detail_test(testSets, testLabels, scores, fWords, label_feature):
    docCounts, features = label_feature, fWords
    docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
    rCount = 0
    docCount = 0
    pCount = 0
    nCount = 0
    p = 0
    n = 0
    print("==============Testing=============")
    for j in range(len(testSets)):
        text = testSets[j]
        label = testLabels[j]
        preValues = list(docScores)
        for word in text:
            if word in scores.keys():
                for i in range(len(preValues)):
                    preValues[i] += math.log(scores[word][i])
        m = max(preValues)
        v = preValues.index(m)
        print("===========news, label, prediction=============")
        print(text, label, v)
        if int(v) == int(label):
            rCount += 1
        if int(label) == 1:
            p += 1
            if int(v) == 1: pCount += 1
        if int(label) == 0:
            n += 1
            if int(v) == 0: nCount += 1
        docCount += 1
    print("===========Testing Finish==========")
    print("Test Sample: %d" % docCount)
    print("Correct sample: %d" % rCount)
    print("Accuracy: %s" % str(rCount/docCount))
    print("Positive Accuracy: %s" % str(pCount/p))
    print("Negative Accuracy: %s" % str(nCount/n))

def get_test_data(filename):
    testData = []
    testLabel = []
    dicts = read_to_dict(filename)
    for single_dict in dicts.values():
        single_dict = eval(single_dict)
        for key, value in single_dict.items():
            testData.append(value)
            testLabel.append(key)
    return testData, testLabel

def save_model(scores, fWords, label_feature):
    for key, value in scores.items():
        scores[key] = {0: value[0], 1:value[1]}
    write_to_csv(scores, model_path+"/scores.csv", ['word', 'probability'])
    fw = open(model_path+"/wordLabel.txt", 'w')
    for word in fWords:
        fw.write(word+",")
    fw.write("\n")
    fw.write(str(label_feature[0]) + "," + str(label_feature[1]) + "\n")
    fw.close()
    print("=======save model ok=========")

def load_model():
    scores = read_to_dict(model_path+"/scores.csv")
    for key, value in scores.items():
        value = eval(value)
        scores[key] = list(value.values())
    fr = open(model_path+"/wordLabel.txt")
    line = fr.readlines()
    fWords = line[0].strip().split(',')
    label_feature = [0]*2
    label_feature[0] = int(line[1].strip().split(',')[0])
    label_feature[1] = int(line[1].strip().split(',')[1])
    return scores, fWords, label_feature

def construct_info():
    return {0:0, 1:0}

def train_naive(datasets, labels):
    word_feature = defaultdict(construct_info)
    label_feature = [0]*2
    # fw = open(path+"/feature.txt", 'w')
    print("===========Extracting features.....=============")
    for i in range(len(datasets)):
        label = int(labels[i])
        dataset = datasets[i]
        for word in dataset:
            word_feature[word][label] += 1
            label_feature[label] += 1
    write_to_csv(word_feature, path+"/feature.txt", ['word', 'info'])
    print("===========Writing features....===================")
    write_test_data({'#':{0:label_feature[0], 1:label_feature[1]}}, path+'/feature.txt', ['TOTAL', 'message'])
    word_naive = defaultdict(construct_info)
    for word in word_feature:
        # and  (0.5 - (word_feature[word][0]/(word_feature[word][0] + word_feature[word][1])))>0.05
        if (word_feature[word][0] + word_feature[word][1]) >= 2:
            for label in range(0,2):
                word_naive[word][label] = (word_feature[word][label]*1.0 + 1 ) / (label_feature[label] + len(word_feature))
    return word_naive, label_feature

def predict_naive(text, word_naive, label_feature):
    # docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
    # print("==============Predicting===========")
    # preValues = list(docScores)
    p = label_feature[0]*1.0/(label_feature[0]+label_feature[1])
    n = 1 - p
    prepredict = [math.log(p),math.log(n)]
    for word in text:
        if word in word_naive:
            prepredict[0] += math.log(word_naive[word][0])
            prepredict[1] += math.log(word_naive[word][1])
    return prepredict.index(max(prepredict))

def test_naive(testSets, testLabels, word_naive, label_feature):
    c = 0
    p, n, pCount, nCount = 0, 0, 0, 0
    for testSet, testLabel in zip(testSets, testLabels):
        predicted = predict_naive(testSet, word_naive, label_feature)
        if predicted == testLabel:
            c += 1
        if testLabel == 1:
            pCount += 1
            if predicted == 1: p += 1
        else:
            nCount += 1
            if predicted == 0: n += 1
    print("=====analysis finish=======")
    print("Accuracy %s" % str(c/len(testSets)))
    print("Positive Accuracy %s" % str(p/pCount))
    print("Negative Accuracy %s" % str(n/nCount))



def test_single_day():
    import time
    news_path = test_path+"/test_data_telegram.csv"
    current_time = int(time.time())
    step_time = 12*60*60
    pointer = 0
    news = read_to_dict(news_path)
    batch = defaultdict(list)
    for key, value in news.items():
        v = eval(value)
        h = int((current_time-int(v['time']))/step_time)
        batch[h].append((int(v['flag']), v['title']))
        # else:
        #     # current_time -= int((current_time - int(v['time'])) / step_time) * step_time
        #     # print(current_time, v['time'])
        #     while  current_time - step_time > int(v['time']):
        #         current_time -= step_time
        #     batch[current_time].append((int(v['flag']), v['title']))

    scores, fWords, label_feature = load_model()

    print("=======synthesis test===========")
    print("=======timestamp====number of news======correct classification=====")
    Accuracy_count = 0
    Total_count = 0
    for time_s, news in batch.items():
        correct = 0
        total = 0
        Total_count += 1
        for info in news:
            total += 1
            new = info[1]
            flag = info[0]
            predicted = predict_naive(new, scores, label_feature)
            if predicted == flag:
                correct += 1
        print(time_s, total, correct)
        if correct >= int(total/2):
            Accuracy_count += 1
    print("==========synthesis tes analysis=========")
    print("TEST SAMPLE:", Total_count)
    print("CORRECT SAMPLE:", Accuracy_count)
    print("ACCURACY:", Accuracy_count/Total_count)

def test_whole_model():
    import time
    import collections
    news_path = path+"/after_test.csv"
    current_time = int(time.time())
    step_time = 12*60*60
    pointer = 0
    news = read_to_dict(news_path)
    batch = collections.defaultdict(list)
    for key, value in news.items():
        v = eval(value)
        if  current_time - step_time <= v['time'] <= current_time:
            batch[current_time].append((int(v['flag']), v['news']))
        else:
            current_time -= step_time

    scores, fWords, label_feature = load_model()

    print("=======synthesis test===========")
    # print("=======timestamp====number of news======correct classification=====")
    Accuracy_count = 0
    Total_count = 0
    for time_s, news in batch.items():
        correct = 0
        total = 0
        Total_count += 1
        for info in news:
            total += 1
            new = info[1]
            flag = info[0]
            predicted = predict_naive(new, scores, label_feature)
            if predicted == flag:
                correct += 1
        # print(time_s, total, correct)
        if correct > int(total/2):
            Accuracy_count += 1
    print("==========synthesis tes analysis=========")
    print("TEST SAMPLE:", Total_count)
    print("CORRECT SAMPLE:", Accuracy_count)
    print("ACCURACY:", Accuracy_count/Total_count)


def processDataForTestModel():
    filename = path + "/after_washed_test.csv"
    dict_name = father_path + "/backup.csv"
    dict = read_to_dict(dict_name)
    news = read_to_dict(filename)
    for key, value in dict.items():
        v = eval(value)
        v['news'] = list(eval(news[key]).values())[0]
        v['flag'] = list(eval(news[key]).keys())[0]
        dict[key] = v
    write_to_csv(dict, path+"/after_test.csv", ['number', 'new'])
    print("=======generate series news ok=========")


def test_bayes():
    # news_path = path + "/origin_news_data.csv"
    news_path = father_path + "/origin_news_data.csv"
    # #---------
    # generate_wordmessage(news_path)
    vocabulary = create_vocabulary(path+"/word_message.csv", 4)
    posts_list, classes_list = get_origin_data(news_path, vocabulary)
    total_len = len(classes_list)
    basic_set = [i for i in range(0, total_len)]
    random.shuffle(basic_set)
    train_test_ratio = 0.8
    train_posts = [posts_list[i] for i in basic_set[0:int(total_len*train_test_ratio)]]
    train_labels = [classes_list[i] for i in basic_set[0:int(total_len*train_test_ratio)]]
    test_posts = [posts_list[i] for i in basic_set[int(total_len*train_test_ratio):]]
    test_labels = [classes_list[i] for i in basic_set[int(total_len * train_test_ratio):]]
    # w_n, l_f = train_naive(train_posts, train_labels)
    # printx(w_n)
    # test_naive(test_posts, test_labels, w_n, l_f)
    fWords, label_feature = genFeature(train_posts, train_labels)
    scores = train_bayes(fWords, train_posts, train_labels, label_feature)
    save_model(scores, fWords, label_feature)
    #---------

    #-----------------test--------------------

    print("==========load model ok========")
    # testData, testLabel = get_test_data(father_path + "/test_data/test_news.csv")
    # test_model(testData, testLabel, scores, fWords, label_feature)
    #
    # testData, testLabel = get_test_data("test_cnn_news.csvßß
    test_model(train_posts, train_labels, scores, fWords, label_feature)


def unitTestBayes():
    news_path = father_path + "/test_data/test_data.csv"
    vocabulary = create_vocabulary(path+"/word_message.csv", 4)
    posts_list, classes_list = get_origin_data(news_path, vocabulary)
    scores, fWords, label_feature = load_model()
    # h = random.randint(1, len(posts_list)-10)
    # posts_list, classes_list = posts_list[h:10+h], classes_list[h:10+h]
    detail_test(posts_list, classes_list, scores, fWords, label_feature)

def unitTestBayes2():
    news_path = father_path + "/test_data/test_data.csv"
    vocabulary = create_vocabulary(path+"/word_message.csv", 4)
    posts_list, classes_list = getTestNews(news_path, vocabulary)
    scores, fWords, label_feature = load_model()
    # h = random.randint(1, len(posts_list)-10)
    # posts_list, classes_list = posts_list[h:10+h], classes_list[h:10+h]
    detail_test(posts_list, classes_list, scores, fWords, label_feature)

if __name__ == "__main__":
    import time
