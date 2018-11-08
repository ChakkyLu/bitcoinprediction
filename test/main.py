from naiveBayes import *
import sys
sys.path.append("..")
from prediction.naiveBayes import BayesModel as BayesModel
from prediction.LSTM import lstmModel as lstmModel
from base.generate_orgin_data import *
from base.preprocessing_newsdata import *
from LSTM import *


class Solution():
    def __init__(self):
        self.bookPath = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"
        self.dataPath = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/data/train_data/trainNews.csv"
        self.trainSet = []
        self.trainLabel = []
        self.book = []
        pass

    def getVocabulary(self):
        bookFile = open(self.bookPath)
        bookContent = bookFile.readlines()
        book = bookContent[0].split(',')[:-1]
        bookFile.close()
        self.book = book

    def genData(self):
        labels = []
        news = []
        self.getVocabulary()
        dicts = read_to_dict(self.dataPath)
        for single_dict in dicts.values():
            value = eval(single_dict)
            vt = list(value['title'])
            for word in vt:
                if word not in self.book:
                    vt.remove(word)
            if len(vt)!=0:
                news.append(vt)
                labels.append(int(value['flag']))
        self.DataSet = news
        self.Labels = labels



if __name__ == "__main__":
    # G = GenerateData(threshold=0.001)
    # G.labelTrainData(12, True, 1)

    M = Solution()
    M.genData()
    # print(M.DataSet)
    TRAIN_RATIO = 0.7
    B = BayesModel(TRAIN_RATIO=TRAIN_RATIO, dataSet=M.DataSet, dataLabel=M.Labels, label=[-1,0,1])
    B.train_bayes()
    # B.save_model()
    # B.load_model()
    B.model_analysis()




    # get_origin_data(12*60, 0)
    # change_interval_influence()
    # get_current_news(5,0)
    # test_bayes()
    # reWashNews()
    # unitTestBayes()
    # getBitcoin()
    # lstm()
    # up_down_test()

    # test_bayes()

    # get_test_news(12*60, 0, latest=True)
    # unitTestBayes()
