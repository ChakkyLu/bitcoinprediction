import spacy
import datetime
from nltk.corpus import wordnet
from nltk.metrics import *
from nltk import word_tokenize
import os
import nltk
from .csv_operation import *
import sys
from collections import defaultdict
import pandas as pd
import numpy as np
import pickle
import re


STOPLIST = ["'", '"', ',', "’", '-']
nlp = spacy.load('en')
processed_time = []
first_processed_words = []


def wash_word(book, word):
    sword = str(word)
    for c in STOPLIST:
        while c in sword:
            if sword.index(c) == 0: sword = sword[1:]
            else:
                if sword.index(c) == len(sword) - 1: sword = sword[0:-1]
                else:
                    sword = sword[0:sword.index(c)] + sword[sword.index(c)+1:]
    word = nlp(sword)
    for token in word:
        if str(token).isalpha() and len(token)>=2:
            if not re.search('pron', str(token.lemma_),  flags=re.IGNORECASE):
                return reduceSynonyms(book, token.lemma_)
    return None


def reduceSynonyms(book, word):
    if not isinstance(word, str):
        word = str(word)
    for syn in wordnet.synsets(word):
        for name in syn.lemma_names():
            if name in book:
                return name
    return word

def getVocabulary():
    bookName = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"
    bookFile = open(bookName)
    bookContent = bookFile.readlines()
    book = bookContent[0].split(',')[:-1]
    bookFile.close()
    return book

def preprocessing_newsdata(titles, updateTime, mode):

    book = getVocabulary()

    processedTitles = []
    processedTimes = []

    for title in titles:
        data = nlp(title)
        tmpTitle = []
        for token in data:
            if not token.is_stop and not token.is_punct:
                ap = wash_word(book, token.lemma_)
                if ap:
                    tmpTitle.append(ap)
        processedTitles.append(tmpTitle)

    if mode == 1:
        for time_element in update_time:
            processedTimes.append(datetime.datetime.strptime(time_element, '%B %d, %Y %H:%M').timestamp())
    else:
        processedTimes = updateTime

    print("=====washing finsihed=======")

    return processedTitles, processedTimes



def generateVocab():
    print("====start generating vocabulary=====")

    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'

    news = read_to_dict(datapath+"/backup.csv")

    book = []

    i = 0
    news = list(news.values())
    n = len(news)


    for new in news:
        title = eval(new)['news']

        data = nlp(title)

        i += 1

        for token in data:
            if not token.is_stop and not token.is_punct:
                ap = wash_word(book, token.lemma_)

        sys.stdout.write("\rProgress %s / %s" % (i,n+1))
        sys.stdout.flush()


    bookName = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"

    fw = open(bookName, 'w')

    for word in book:
        print(word)
        fw.write(word+",")

    fw.write("\n")
    fw.close()


    print("=====vocabulary generated=======")

def shrinkBookSize():
    bookName = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"

    bookFile = open(bookName)

    book = bookFile.readlines()[0].strip().split(',')[:-1]


    newBook = []
    i = 0

    while i < len(book):
        word1 = book[i]
        if word1 in newBook:
            i += 1
            continue
        word = nlp(word1)
        for w in word:
            if w.is_stop or w.is_punct:
                break
            else:
                newBook.append(word1)
        i += 1
        sys.stdout.write("\rProgress %s / %s" % (i,len(book)))
        sys.stdout.flush()

    bookFile.close()

    bookName = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"

    fw = open(bookName, 'w')

    for word in newBook:
        fw.write(word+",")
    fw.write("\n")
    fw.close()

def reduceSimilarityByDistance():
    bookName = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/model/book.txt"

    bookFile = open(bookName)

    bookContent = bookFile.readlines()
    book = []

    for bookcontent in bookContent:
        bookcontent = bookcontent.strip().replace(',', '')
        book.append(bookcontent)

    i = 0

    bookFile.close()
    bookFile = open(bookName, 'w')

    for word in book:
        token = nlp(word)
        if token:
            bookFile.write(word+",")

    bookFile.write("\n")

    bookFile.close()

    length = len(book)

#---------------------calculate jaccard_distance----------------
    # wordDistance = defaultdict()
    # with open('test.pkl','rb') as f:
    #      Distance = pickle.load(f)
    #
    # h = list(np.argmin(Distance, axis=0))
    #
    # for i in range(length):
    #     print("===original=====similarity")
    #     print(book[i], book[h[i]], Distance[i][h[i]])
    #
    # Distance = np.zeros((length, length))
    #
    # while i <  len(book):
    #
    #     word1 = book[i]
    #     wordDistance[word1] = [0]*length
    #
    #     j = 0
    #
    #     sys.stdout.write("\r Progress %s / %s " % (i,len(book)))
    #     sys.stdout.flush()
    #
    #
    #
    #     while j < len(book):
    #         if i == j: wordDistance[word1][j] = 1
    #         else:
    #             word2 = book[j]
    #             s1 = set(word1)
    #             s2 = set(word2)
    #             # print(word1, word2, jaccard_distance(s1, s2))
    #             wordDistance[word1][j] = jaccard_distance(s1, s2)
    #         Distance[i][j] = wordDistance[word1][j]
    #         j += 1
    #         # sys.stdout.write("\rProgress %s / %s" % (j,len(book)))
    #         # sys.stdout.flush()
    #     i += 1
    #
    # print("\n")
    #
    # write_to_csv(wordDistance, "test.csv", ['word', 'distance'])
    #
    # with open('test.pkl','wb') as f:
    #     pickle.dump(Distance, f)

if __name__ == "__main__":
    shrinkBookSize()
# if mode == 0:
#     for time_element in update_time:
#         processed_time.append(datetime.datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S+00:00').timestamp())
