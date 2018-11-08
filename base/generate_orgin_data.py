import os
import time
from .preprocessing_newsdata import *
from .news_grabber import *
from .price_grabber import get_poloniex_data
from collections import defaultdict
from .csv_operation import read_to_dict, write_to_csv, write_test_data
from .scrape_news import *
import numpy as np


class GenerateData():

    def __init__(self, threshold=0.005, timeEffect=1):
        self.path = os.path.abspath(os.path.join(os.getcwd(), ".."))
        self.threshold = threshold
        self.timeEffect = timeEffect * 3600
        pass


    def percentage_change(self, percentage):
        change = round(percentage, 1)
        return change


    def altitude_word(self, processed_titles, change):
        title_classifier_dict = defaultdict(list)
        title_word_dict = {}
        for i, title in enumerate(processed_titles):
            for word in title:
                title_classifier_dict[word].append(change[i])
        for key, value in title_classifier_dict.items():
            title_word_dict[key] = len(value)
        return title_word_dict

    def getVocabulary(self):
        vocabFile = self.path + "/model/book.txt"
        with open(vocabFile) as f:
            books = f.readlines()[0].split(',')[:-1]
        self.books = books

    def getPriceDict(self):
        priceFile = self.path + "/model/bitcoin_price.csv"
        priceDict = read_to_dict(priceFile)
        priceDictLen = len(priceDict)
        i = 0
        priceArr = np.zeros((priceDictLen,2))
        for key,value in priceDict.items():
            priceArr[i][0] = key
            priceArr[i][1] = value
            i += 1
        self.priceArr = []
        for i in range(0, priceDictLen, int(self.timeEffect/300)):
            rows = np.arange(i, min(i+int(self.timeEffect/300), priceDictLen))
            tmp = priceArr[rows, [1]]
            tmp = np.average(tmp)
            self.priceArr.append([priceArr[i][0],tmp])
        self.priceArr = np.array(self.priceArr)
        print("============Generate Price Matrix Success=========")

    def getNearestTime(self, updateTIme):
        n = self.priceArr.shape[0]
        times = np.array([updateTIme])
        times = np.tile(times, (n, 1))
        timeNeighbour = self.priceArr[:,0].reshape(n,1) - times
        fitIndex = np.where(timeNeighbour >= 0 )
        return self.priceArr[fitIndex[0][0],1]

#-----------------Label the news---------------
# '''
#     parameter:
#         updateTIme: the time news published
#     variable:
#         effectTime: the time used for label the news // use [timePeriod] to control the effectTime
#     returnData:
#         {
#             1: the price increment exceeds the threshold(which in model's parameter)
#             -1: the price decresement exceeds the threshold
#             0: the price is in normal fluctuation
#         }
# '''

    def getNewsTag(self, updatedTime):
        currentTime = updatedTime
        effectTime = updatedTime + self.timePeriod
        currentPrice = self.getNearestTime(currentTime)
        nextPrice = self.getNearestTime(effectTime)
        change = (nextPrice - currentPrice)/currentPrice
        if change >= self.threshold:
            return (1, self.percentage_change(change*100))
        if change <= -self.threshold:
            return (-1, self.percentage_change(change*100))
        return (0, self.percentage_change(change))

#----------------For train-----------------
    # time_period: classify news every 60*time_period seconds
    # mode: {
    #     0: from news.bitcoin.com
    #     1: from ccn.com
    # }
    # extraClass:{
    #     true: up, down, same three classes
    #     false: up or down
    # }
#-------------------------------------------

    def get_origin_data(self, time_period, mode, extraClass=False):
        self.timePeriod = time_period * 3600
        datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
        if mode == 0:
            titles, update_time = scrape_newsbitcoin(500, 0)
        if mode == 1:
            titles, update_time = grabber_ccn(500, 0)
        processed_titles, processed_time = preprocessing_newsdata(
            titles, update_time, mode)
        news_data = {}

        for i in range(len(processed_time)):
            news_data[i] = {'time': processed_time[i], 'news': titles[i]}
        write_to_csv(news_data, datapath+"/backup.csv", ['time', 'news'])

        print("==========Grab News Finish=========")
        btc_chart_data = get_poloniex_data('USDT_BTC', 5*60, 1506816000)
        btc_chart_data.set_index('date', inplace=True)
        percentage_changes = []
        round_up_percentage_changes = []
        flag_change = []

        for time in processed_time:
            now = btc_chart_data.iloc[
                btc_chart_data.index.get_loc(time, method='nearest')]['close']

            after = btc_chart_data.iloc[
                btc_chart_data.index.
                    get_loc(time, method='nearest')+int(time_period/5)]['close']

            price_change = (after - now) / now * 100

            percentage_changes.append(price_change)
            round_up_percentage_changes.append(percentage_change(price_change))
            if not extraClass:
                flag_change.append(1) if price_change > 0.0 else flag_change.append(0)
            else:
                if price_change == 0.0: flag_change.append(0)
                if price_change > 0.0: flag_change.append(1)
                else:   flag_change.append(-1)

        origin_news_tag = {}

        for i in range(len(processed_titles)):
            origin_news_tag[i] = {flag_change[i]: processed_titles[i]}
        write_to_csv(origin_news_tag, datapath+"/origin_news_data.csv", ['flag', 'news'])
        print("==========Obtain Original Data Finish=========")

        # -------------altitude word: deprecated now---------------
        flag_classifier_dict = altitude_word(processed_titles, flag_change)
        write_to_csv(flag_classifier_dict, datapath+"/word_message.csv", ['word', 'message'])


#----------------labelTrainData-----------------
# '''
#     BETA 2.0
#     For labeling the news for training
#     parameters:
#         time_period: after how much time, the given news will effect the price
#         extraClass: {
#                         True: use thress labels: [-1,0,1]
#                         False: use two labels: [0,1]
#                     }
#         mode: {
#            1 : need process news
#            0: dont need process news
#        }
#     variables:
#         updateTime: news updateTime
#         titles: news titles
#
# '''

#-------------------------------------------

    def labelTrainData(self, timePeriod, extractClass=False, mode=1):

        self.timePeriod = timePeriod * 3600

        datapath = self.path + '/data'
        if mode:
            initialNews = read_to_dict(datapath+'/backup.csv')
        else:
            initialNews = read_to_dict(datapath+'/train_data/trainNews.csv')

        updateTimes, titles= [], []

        for key, value in initialNews.items():
            value = eval(value)
            updateTimes.append(value['time'])
            titles.append(value['news'])

        # sys.stdout.write("[%-20s] %d%%" % ('='*5, 20))
        # sys.stdout.flush()

        print("=========Get previous data ok==========")

        if mode:
            titles, updateTimes = preprocessing_newsdata(titles, updateTimes, 2)

        self.getPriceDict()

        percentageChange = []
        flag = []

        for time in updateTimes:

            flags = self.getNewsTag(time)
            percentageChange.append(flags[1])
            flag.append(flags[0])

        origin_news_tag = {}

        for i in range(len(flag)):
            origin_news_tag[i] = {'flag': flag[i], 'title': titles[i], 'percentage': percentageChange[i], 'timestamp': updateTimes[i]}
        write_to_csv(origin_news_tag, datapath + "/train_data/trainNews.csv", ['number', 'detail'])
        print("==========Label Original Data Finish=========")

#----------------get_current_news-----------------
    # In order to get latest news to predict current price change
    # time_period: classify news every 60*time_period seconds
    # mode: {
    #     0: from news.bitcoin.com
    #     1: from ccn.com
    # }
#-------------------------------------------

    def get_current_news(self, time_period, mode):
        cur_time = int(time.time())
        step_time = time_period*60
        if mode == 0:
            titles, update_time = getLatestNews(10, 1)
        if mode == 1:
            titles, update_time = grabber_ccn(10, 1)
        if mode == 2:
            titles, update_time = getTweet()
            test_filename = "test_data_tweet.csv"
        if mode == 3:
            titles, update_time = cointele()
            test_filename = "test_data_telegram.csv"

        processed_titles, _ = preprocessing_newsdata(
            titles, update_time, 2)

        print("==========Grab Current News Finish=========")
        prices = {}
        end_time = cur_time
        count = 20
        btc_chart_data = get_poloniex_data('USDT_BTC', 300, cur_time-step_time*count)
        btc_chart_data.set_index('date', inplace=True)
        while count:
            price = btc_chart_data.iloc[
                btc_chart_data.index.get_loc(end_time, method='nearest')]['high']
            prices[end_time] = price
            end_time -= step_time
            count -= 1
        print("======Grab previous price OK======")

        cur_news = {}
        for i in range(len(processed_titles)):
            cur_news[i] = processed_titles[i]

        datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
        write_to_csv(cur_news, datapath+"/current_news.csv", ['num', 'news'])
        write_to_csv(prices, datapath+"/previous_price.csv", ['date', 'price'])

#----------------get_test_news-----------------
    # to test the model, extract news from other website
    # mode: {
    #     0: news.bitcoin.com
    #     1: CCN.com
    #     2: twitter.com
    #     4: cointelegraph.com
    #     5: google.com
    # }
    # extraClass:{
    #     true: up, down, same three classes
    #     false: up or down
    # }
#-------------------------------------------

    def get_test_news(self, time_period, mode, extraClass=False, latest=True):
        import time
        cur_time = int(time.time())
        end_time = cur_time
        step_time = time_period*60

        if mode == 0:
            if not latest:
                titles, update_time = scrape_newsbitcoin(10, 0)
            else:
                titles, update_time = getLatestNews(1)
            test_filename = "test_data.csv"
        if mode == 1:
            titles, update_time = grabber_ccn(40, 0)
            test_filename = "test_data.csv"
        if mode == 2:
            titles, update_time = getTweet()
            test_filename = "test_data_tweet.csv"
        if mode == 3:
            titles, update_time = cointele()
            test_filename = "test_data_telegram.csv"

        print("============Grab test news ok==========")

        processed_titles, processed_time = preprocessing_newsdata(
            titles, update_time, mode)

        early_time = int(processed_time[-1])


        print("==========Process test News OK=========")

        interval = 300
        btc_chart_data = get_poloniex_data('USDT_BTC', interval, early_time)
        btc_chart_data.set_index('date', inplace=True)
        percentage_changes = []
        round_up_percentage_changes = []
        flag_change = []


        for time in processed_time:
            time = int(time)
            now = btc_chart_data.iloc[
                btc_chart_data.index.get_loc(time, method='nearest')]['close']

            # time = time + step_time

            try:
                after = btc_chart_data.iloc[
                    btc_chart_data.index.
                        get_loc(time, method='nearest') + int(step_time/interval)]['close']
            except:
                after = btc_chart_data.iloc[
                    btc_chart_data.index.
                        get_loc(time, method='nearest')]['close']

            price_change = (after - now) / now * 100

            percentage_changes.append(price_change)
            round_up_percentage_changes.append(percentage_change(price_change))

            if not extraClass:
                flag_change.append(1) if price_change > 0.0 else flag_change.append(0)
            else:
                if price_change == 0.0: flag_change.append(0)
                if price_change > 0.0: flag_change.append(1)
                else:   flag_change.append(-1)


        origin_news_tag = {}

        for i in range(len(processed_titles)):
            origin_news_tag[i] = { 'flag': flag_change[i], 'title': processed_titles[i], 'time': processed_time[i]}
        datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/test_data/'
        write_to_csv(origin_news_tag, datapath+test_filename, ['number', 'detail'])

        # write_to_csv(prices, datapath + "/previous_price.csv", ['date', 'price'])

        print("==========Obtain test Data Finish=========")


#----------------reWashNews-----------------
    # in order to wash the orginal news for training
    # Need to improve
#-------------------------------------------
    def reWashNews(self):
        time_period = 2*60*60
        datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
        dicts = read_to_dict(datapath+'/test_backup.csv')
        previous_news = read_to_dict(datapath+'/origin_news_data.csv')
        update_time, titles = [], []

        for key, value in dicts.items():
            value = eval(value)
            update_time.append(value['time'])
            titles.append(value['news'])

        processed_titles, processed_time = preprocessing_newsdata(
            titles, update_time, 2)

        # update_time = update_time[6:]
        # titles = titles[60:]

        print("=========Get previous data ok==========")
        btc_chart_data = get_poloniex_data('USDT_BTC', time_period, 1486710000)
        btc_chart_data.set_index('date', inplace=True)
        percentage_changes = []
        round_up_percentage_changes = []
        flag_change = []

        for time in update_time:
            now = btc_chart_data.iloc[
                btc_chart_data.index.get_loc(time, method='nearest')]['close']

            after = btc_chart_data.iloc[
                btc_chart_data.index.
                    get_loc(time+time_period, method='nearest')]['close']

            price_change = (after - now) / now * 100

            percentage_changes.append(price_change)
            round_up_percentage_changes.append(percentage_change(price_change))
            flag_change.append(1) if price_change > 0.0 else flag_change.append(0)

        origin_news_tag = {}

        for i in range(len(flag_change)):
            origin_news_tag[i] = {flag_change[i]: processed_titles[i]}
        write_to_csv(origin_news_tag, datapath + "/train_data/afterwashed.csv", ['flag', 'news'])
        print("==========Obtain Original Data Finish=========")
#
