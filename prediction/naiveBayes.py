import os
import sys
sys.path.append("..")
from base.csv_operation import *
import math
import random
from collections import defaultdict


class BayesModel():
    def __init__(self, TRAIN_RATIO=1.0, model_path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/model/', data_path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/', dataSet=None, dataLabel=None, label=None):
        self.model_path = model_path
        self.data_path = data_path
        self.TRAIN_RATIO = TRAIN_RATIO
        self.dataSet = dataSet
        self.dataClass = dataLabel
        self.labels = label
        assert isinstance(self.dataSet, list) and len(self.dataSet), "ONLY SUPPORT LIST DATATYPE"
        assert isinstance(self.dataClass, list) and len(self.dataClass), "ONLY SUPPORT LIST DATATYPE"
        assert isinstance(self.labels, list) and len(self.labels), "LABEL OF LIST TYPE NEED"
        total_len = len(self.dataClass)
        basic_set = [i for i in range(0, total_len)]
        random.shuffle(basic_set)
        self.trainSet = [self.dataSet[i] for i in basic_set[0:int(total_len * self.TRAIN_RATIO)]]
        self.trainLabel = [self.dataClass[i] for i in basic_set[0:int(total_len * self.TRAIN_RATIO)]]
        self.testSet = [self.dataSet[i] for i in basic_set[int(total_len * self.TRAIN_RATIO):]]
        self.testLabel = [self.dataClass[i] for i in basic_set[int(total_len * self.TRAIN_RATIO):]]
        self.reverse_dict()


    def mutual_info(self, m, n, p, q):
        return n * 1.0 / m * math.log(m, (n + 1) * 1.0 / (p * q)) / math.log(2)

    def construct_dict(self):
        return [0] * len(self.labels)

    def reverse_dict(self):
        self.reverse_label_dict = {}
        self.label_dict = {}
        n = len(self.labels)
        for i in range(n):
            self.label_dict[self.labels[i]] = i
            self.reverse_label_dict[i] = self.labels[i]

    def __prepare(self):
        print("===========Prepare For Train Model=============")
        fw = open(self.model_path + "feature.txt", 'w')
        word_feature = defaultdict(self.construct_dict)
        label_feature = self.construct_dict()

        for i in range(len(self.dataSet)):
            tag = int(self.dataClass[i])
            dataset = self.dataSet[i]
            for word in dataset:
                label = self.label_dict[tag]
                word_feature[word][label] += 1
                label_feature[label] += 1
        mDict = defaultdict(self.construct_dict)
        N = sum(label_feature)
        for k, vs in word_feature.items():
            for i in range(len(vs)):
                N11 = vs[i]
                N10 = sum(vs) - N11
                N01 = label_feature[i] - N11
                N00 = N - N11 - N10 - N01
                mi = self.mutual_info(N, N11, N10 + N11, N01 + N11) + self.mutual_info(N, N10, N10 + N11,
                                                                                       N00 + N10) + self.mutual_info(N, N01, N01 + N11,
                                                                                                                     N01 + N00) + self.mutual_info(
                    N, N00, N00 + N10, N00 + N01)
                mDict[k][i] = mi
        fWords = set()
        for i in range(len(label_feature)):
            keyf = lambda x: x[1][i]
            sortedDict = sorted(mDict.items(), key=keyf, reverse=True)
            for j in range(len(sortedDict)):
                fWords.add(sortedDict[j][0])
                fw.write(sortedDict[j][0] + ",")
        fw.write("\n")
        label_value = ','.join(str(l) for l in label_feature)
        fw.write(label_value+ "\n")
        self.fWords = fWords
        self.label_feature = label_feature
        fw.close()


    def train_bayes(self):
        print("=========Training Model===========")
        self.__prepare()
        wordCount = defaultdict(self.construct_dict)
        docCounts = self.label_feature
        tCount = [0] * len(docCounts)
        for i in range(len(self.trainSet)):
            tag, text = self.trainLabel[i], self.trainSet[i]
            for word in text:
                if word in self.fWords:
                    label = self.label_dict[tag]
                    tCount[label] += 1
                    wordCount[word][label] += 1
        scores = {}

        for k, v in wordCount.items():
            score = [(v[i] + 1) * 1.0 / (tCount[i] + len(wordCount)) for i in range(len(v))]
            scores[k] = score
        self.scores = scores
        self.train_loss()

    def construct_eval_dict(self):
        evaluate = defaultdict()
        for label in self.labels:
            evaluate[label] = self.construct_dict()
        return evaluate

    def adjust_word_weights(self):
        pass


    def train_loss(self):
        print("=========Train Loss=============")

        docCounts, features = self.label_feature, self.fWords
        docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
        rCount = 0
        docCount = 0

        tEvaluate = self.construct_eval_dict()

        for j in range(len(self.trainSet)):
            text = self.trainSet[j]
            label = self.trainLabel[j]
            preValues = list(docScores)
            for word in text:
                if word in self.scores.keys():
                    for i in range(len(preValues)):
                        preValues[i] += math.log(self.scores[word][i])
            m = max(preValues)
            v = preValues.index(m)
            v = self.reverse_label_dict[v]
            tEvaluate[v][self.label_dict[label]] += 1

            if int(v) == int(label):
                rCount += 1

            docCount += 1
        print("TRAIN LOSS: %s" % str(rCount / docCount))
        print("POSITIVE:")
        print("\tLOSS: %s" % str(tEvaluate[1][self.label_dict[1]]/sum(tEvaluate[1])))
        print("\tREDIRECT TO NEGATIVE: %s" % str(tEvaluate[1][self.label_dict[-1]]/sum(tEvaluate[1])))
        print("\tREDIRECT TO STABLE: %s" % str(tEvaluate[1][self.label_dict[0]]/sum(tEvaluate[1])))

        print("STABLE:")
        print("\tLOSS: %s" % str(tEvaluate[0][self.label_dict[0]]/sum(tEvaluate[0])))
        print("\tREDIRECT TO POSTIVE: %s" % str(tEvaluate[0][self.label_dict[-1]]/sum(tEvaluate[0])))
        print("\tREDIRECT TO NEGATIVE: %s" % str(tEvaluate[0][self.label_dict[1]]/sum(tEvaluate[0])))

        print("NEGATIVE:")
        print("\tLOSS: %s" % str(tEvaluate[-1][self.label_dict[-1]]/sum(tEvaluate[-1])))
        print("\tREDIRECT TO POSITIVE: %s" % str(tEvaluate[-1][self.label_dict[1]]/sum(tEvaluate[-1])))
        print("\tREDIRECT TO STABLE: %s" % str(tEvaluate[-1][self.label_dict[0]]/sum(tEvaluate[-1])))

    def save_model(self):
        print("===========Save Model==============")
        for key, value in self.scores.items():
            tmp_dict = {}
            for k, v in self.label_dict.items():
                tmp_dict[k] = value[v]
            self.scores[key] = tmp_dict
        write_to_csv(self.scores, self.model_path + "scores.csv", ['word', 'probability'])
        fw = open(self.model_path + "wordLabel.txt", 'w')
        for word in self.fWords:
            fw.write(word + ",")
        fw.write("\n")
        fw.write(str(self.label_feature[0]) + "," + str(self.label_feature[1]) + "\n")
        fw.close()

    def load_model(self):
        scores = read_to_dict(self.model_path+"scores.csv")
        for key, value in scores.items():
            value = eval(value)
            scores[key] = list(value.values())
        fr = open(self.model_path+"/feature.txt")
        line = fr.readlines()
        self.fWords = line[0].split(',')
        self.scores = scores
        label_feature = line[1].split(',')
        label_feature = [int(label) for label in label_feature]
        self.label_feature = label_feature

    def predict_bayes(self, text):
        docCounts, features = self.label_feature, self.fWords
        docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
        preValues = list(docScores)
        for word in text:
            if word in self.fWords:
                for i in range(len(preValues)):
                    preValues[i] += math.log(self.scores[word][i])

        m = max(preValues)
        return preValues.index(m)

    def model_analysis(self):

        docCounts, features = self.label_feature, self.fWords
        docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
        rCount = 0
        docCount = 0

        tEvaluate = self.construct_eval_dict()

        for j in range(len(self.trainSet)):
            text = self.trainSet[j]
            label = self.trainLabel[j]
            preValues = list(docScores)
            for word in text:
                if word in self.scores.keys():
                    for i in range(len(preValues)):
                        preValues[i] += math.log(self.scores[word][i])
            m = max(preValues)
            v = preValues.index(m)
            v = self.reverse_label_dict[v]
            tEvaluate[v][self.label_dict[label]] += 1

            if int(v) == int(label):
                rCount += 1

            docCount += 1
        print("TOTAL ACCURACY: %s" % str(rCount / docCount))
        print("POSITIVE:")
        print("\tACCURACY: %s" % str(tEvaluate[1][self.label_dict[1]]/sum(tEvaluate[1])))
        print("\tNEGATIVE PORPOTION: %s" % str(tEvaluate[1][self.label_dict[-1]]/sum(tEvaluate[1])))
        print("\tSTABLE PORPOTION: %s" % str(tEvaluate[1][self.label_dict[0]]/sum(tEvaluate[1])))

        print("STABLE:")
        print("\tACCURACY: %s" % str(tEvaluate[0][self.label_dict[0]]/sum(tEvaluate[0])))
        print("\tPOSTIVE PORPOTION: %s" % str(tEvaluate[0][self.label_dict[-1]]/sum(tEvaluate[0])))
        print("\tNEGATIVE PORPOTION: %s" % str(tEvaluate[0][self.label_dict[1]]/sum(tEvaluate[0])))

        print("NEGATIVE:")
        print("\tACCURACY: %s" % str(tEvaluate[-1][self.label_dict[-1]]/sum(tEvaluate[-1])))
        print("\tPOSITIVE PORPOTION: %s" % str(tEvaluate[-1][self.label_dict[1]]/sum(tEvaluate[-1])))
        print("\tSTABLE PORPOTION: %s" % str(tEvaluate[-1][self.label_dict[0]]/sum(tEvaluate[-1])))
