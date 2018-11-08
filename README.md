# bitcoinprediction

#### ENGLISH VERSION
-----
#### Introduction
1. It is a model to predict bitcoin price
2. It is based on technique of Nature Language Processing(NLP), naive bayes and Long Short Term Memory networks (LSTM)

#### Decision Origin
1. From past news in area of bitcoin ( collecting from news.bitcoin.com, ccn.com, google.com, twitter and so on
2. Past bitcoin price

#### Instruction
up to 18/11/8
BETA 1.0
TRAIN PART
base:
  scrape_news.py: use for collect news from website based on urllib
  generate_orgin_data.py: get news data or price
  preprocessing_newsdata.py: to process original news title

#### BETA 0.5
    1. scrapping news methods are based on selenium and chromedriver
    DEMERIT: need to update chromedriver in order to cater to the version of chrome browser and low speed
    2. support only two websites for collecting news (news.bitcoin.com and ccn.com)
    3. use spacy package to process news' title (tokenize, lemma, stop word)
    4. use polenix to obtain bitcoin price, time_period which specifies collecting price every how much time
    5. when label the given news, compare the price of datetime which the news updated and the price of time_period plus datetime
    6. only use two kinds of label (postive: price up and negative: price down)
    
##### BETA 1.0
    1. support more choice when collecting news
    up to BETA 1.0, support: news.bitcoin.com, ccn.com, google.com, bitcoin's twitter, cointelegram.com)
    2. use urllib package instead of selenium
    DEMERIT: some error like ads happening may occur, and some news do not provide explicit datetime, need regular  expression process
    MERIT: faster
    3. compared to BETA 0.5, try to create the vocabulary when processing data. use NLTK package to find a given word's     synonyms, and merge similar words (such as 'important' and 'significant') in order to reduce the size of vocabulary
    4. (ATTEMPT) try to calculate the distance between words to further shrink the size of vocabulary,(jaccard distance           failed)
    (ABOVE PROCESS CAN BE FOUND ON preprocessing_newsdata.py)
    5. since bitcoin price is not stable even in a hour. In order to analyze the effect of the given news more precisely, use average of a time interval price instead of single point price. compared to BEAT 0.5, add one more parameter to evaluate the influence taken by news
    6. add one more label meaning stable, and add a parameter to control the threshold which determine the label of news
    
prediction:
  naiveBayes.py: provide the prediction model based on naivebayes
  LSTM.py: provide the prediction model based on LSTM
  
  // BEAT 0.5 vs BETA 1.0:
   not so many changes
   
   naiveBayes: try to analyze the words in news
   
   (ATTEMPT):
   1. use neural network to train the weights of word while naivebayes gives the first weights
   
 
 #### Usage
clone this project to local,
'''
cd bitcoinpredcition
cd test
python main.py
'''
1. the you can see the trainning model's loss and test data's accurarcy

waiting for more usages
 
  
