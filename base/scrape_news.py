import datetime
import urllib.request
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import requests
import datetime
import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
month = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}


def regexTimeRepresent(time_flag):
    import time
    cur_time = int(time.time())

    pattern_ago = 'ago'
    pattern_day = "day"
    pattern_hour = "hour"
    pattern_min = "min"
    timestamp = 0

    if re.search(pattern_ago, time_flag, flags=re.IGNORECASE):
        timeFlag = time_flag.split()
        if re.search(pattern_day, time_flag, flags=re.IGNORECASE):
            timestamp = cur_time - int(timeFlag[0])*24*60*60
        if re.search(pattern_hour, time_flag, flags=re.IGNORECASE):
            timestamp = cur_time - int(timeFlag[0])*60*60
        if re.search(pattern_min, time_flag, flags=re.IGNORECASE):
            timestamp = cur_time - int(timeFlag[0])*60
    else:
        time_flag = time_flag.replace(',', '')
        time_flag = time_flag.split()
        time_flag[0] = time_flag[0].upper()
        d = datetime.date(int(time_flag[-1]),month[time_flag[0]], int(time_flag[1]))
        timestamp = time.mktime(d.timetuple())

    return timestamp

def getLatestNews(mode=0):
    import time

    StopTime = int(time.time()) - 12 * 60 * 60

    url = "https://news.bitcoin.com"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    req.add_header('Host', 'news.bitcoin.com')
    req.add_header('Cookie', ' __cfduid=dc172749a14b781fa5821f8da67c407a01539049207; _ga=GA1.2.1547810722.1539049209; ac_enable_tracking=1; _omappvp=DF3dpnr8LilMv5Mchn2tUvLDrAKGzHhvvLXuTJVhVpLkq4Y9WYkz38ynl0ha1c9udtcNDtXhtPRdZPta5YoFzUBmqkH1fyYB; _gid=GA1.2.388542892.1539573874; om-in7rat0uxlot0pwxsk3m=1539574334531; om-ead4x65bjbjpfiap4zuo=1539574762692; _gat_UA-59964190-1=1')
    req.add_header('Connection', 'keep-alive')

    LOAD_OUT = 50
    while LOAD_OUT:
        try:
            page_info = urllib.request.urlopen(req, context=context)
            break
        except Exception:
            LOAD_OUT -= 1

    page_info = page_info.read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    update_times = []

    for resultTable in soup.find_all('div',class_='td_module_wrap'):
        title = resultTable.find_all('a')[0].get('title')
        h = resultTable.find_all('span', class_="td-post-date ago-date-small")
        if h:
            h = h[0].get_text()
        else:
            h = resultTable.find_all('span', class_="ago-date-small-mx1")
            if h :
                h = h[0].get_text()
            else:
                h = resultTable.find_all('span', class_="latest-left")
                if h:
                    h = h[0].get_text()
                else:
                    h = ""
        if h != "":
            while not h[0].isdigit() and not h[0].isalpha():
                h = h[1:]
            h = regexTimeRepresent(h)
            if h:
                titles.append(title)
                update_times.append(h)
                if mode and h < StopTime:
                    break

    return (titles, update_times)

def GetGoogleNews():
    import time

    StopTime = int(time.time()) - 12 * 60 * 60

    url = "https://www.google.co.jp/search?q=bitcoin&tbm=nws"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    req.add_header('Connection', 'keep-alive')
    LOAD_OUT = 50
    while LOAD_OUT:
        try:
            page_info = urllib.request.urlopen(req, context=context)
            break
        except Exception:
            LOAD_OUT -= 1
            print("====LOAD OUT=====")

    page_info = page_info.read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    update_times = []

    resultTables = soup.find_all('div',class_='g')


    for resultTable in resultTables:
        list1 = resultTable.find_all('div', class_="gG0TJc")
        if list1:
            title = list1[0].find_all(class_="r dO0Ag")
            if title:
                title = title[0].get_text()
                upTime = list1[0].find_all(class_="f nsa fwzPFf")[0].get_text()
                titles.append(title)
                update_times.append(regexTimeRepresent(upTime))
        list1 = resultTable.find_all('div', class_="YiHbdc card-section")
        if list1:
            for innerList in list1:
                title = innerList.find_all(class_="RTNUJf")
                if title:
                    title = title[0].get_text()
                    upTime = innerList.find_all(class_="nsa fwzPFf f")[0].get_text()
                    titles.append(title)
                    update_times.append(regexTimeRepresent(upTime))
    print(titles, update_times)

    return (titles, update_times)

def scrape_newsbitcoin(load_times, mode):
    url = "https://news.bitcoin.com"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    req.add_header('Host', 'news.bitcoin.com')
    req.add_header('Cookie', ' __cfduid=dc172749a14b781fa5821f8da67c407a01539049207; _ga=GA1.2.1547810722.1539049209; ac_enable_tracking=1; _omappvp=DF3dpnr8LilMv5Mchn2tUvLDrAKGzHhvvLXuTJVhVpLkq4Y9WYkz38ynl0ha1c9udtcNDtXhtPRdZPta5YoFzUBmqkH1fyYB; _gid=GA1.2.388542892.1539573874; om-in7rat0uxlot0pwxsk3m=1539574334531; om-ead4x65bjbjpfiap4zuo=1539574762692; _gat_UA-59964190-1=1')
    req.add_header('Connection', 'keep-alive')
    LOAD_OUT = 50
    while LOAD_OUT:
        try:
            page_info = urllib.request.urlopen(req, context=context)
            break
        except Exception:
            LOAD_OUT -= 1

    page_info = page_info.read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    update_times = []
    for resultTable in soup.find_all('div',class_='item-details'):
        titles.append(resultTable.find_all('h3')[0].find_all('a')[0].get('title'))
        update_times.append(resultTable.find_all('time')[0].get('datetime'))

    i = 1
    while i < load_times:
        url = "https://news.bitcoin.com/page/" + str(i) + "/"
        url = "https://news.bitcoin.com/page/2/"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
        req.add_header('Host', 'news.bitcoin.com')
        req.add_header('Cookie', ' __cfduid=dc172749a14b781fa5821f8da67c407a01539049207; _ga=GA1.2.1547810722.1539049209; ac_enable_tracking=1; _omappvp=DF3dpnr8LilMv5Mchn2tUvLDrAKGzHhvvLXuTJVhVpLkq4Y9WYkz38ynl0ha1c9udtcNDtXhtPRdZPta5YoFzUBmqkH1fyYB; _gid=GA1.2.388542892.1539573874; om-in7rat0uxlot0pwxsk3m=1539574334531; om-ead4x65bjbjpfiap4zuo=1539574762692; _gat_UA-59964190-1=1')
        req.add_header('Connection', 'keep-alive')
        while LOAD_OUT:
            try:
                page_info = urllib.request.urlopen(req, context=context)
                break
            except Exception:
                LOAD_OUT -= 1
        page_info = page_info.read()
        html = page_info.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        for resultTable in soup.find_all('div',class_='item-details'):
            titles.append(resultTable.find_all('h3')[0].find_all('a')[0].get('title'))
            times = resultTable.find_all('time')[0].get('datetime')
            times = datetime.datetime.strptime(times, '%Y-%m-%dT%H:%M:%S+00:00').timestamp()
            update_times.append(times)
        i += 1

    return (titles, update_times)

def getTweet():
    update_times = []
    contents = []
    url = "https://twitter.com/BTCTN"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
    page_info = urllib.request.urlopen(req).read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    tweetText = soup.find_all('li', attrs={'data-item-type': 'tweet'})
    for tweet in tweetText:
        content = tweet.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
        timestamp = tweet.find_all('span', class_="_timestamp js-short-timestamp js-relative-timestamp") or tweet.find_all('span', class_="_timestamp js-short-timestamp ")
        if len(content) and len(timestamp):
            content = content[0].get_text()
            timestamp = timestamp[0]
            update_time = timestamp['data-time']
            if 'http' in content:
                content = content[:content.index('http')]
            contents.append(content)
            update_times.append(update_time)
        else: content = ""

    return (contents, update_times)

def cointele():
    import time
    month = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
    cur_time = int(time.time())
    update_times = []
    contents = []
    url = "https://cointelegraph.com/tags/bitcoin"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
    page_info = urllib.request.urlopen(req).read()
    html = page_info.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    tweetText = soup.find_all('div', attrs={'id': 'recent'})[0]
    tweetText = tweetText.find_all('div', class_="row result")
    for tweet in tweetText[:-1]:
        content = tweet.find_all('figure')[1]
        title = content.find_all('h2', class_="header")[0].get_text()
        time_flag = content.find_all('span', class_="date")[0].get_text()
        if 'AGO' in time_flag:
            time_flag = time_flag.split()
            if 'HOUR' in time_flag[1]:
                timestamp = cur_time - int(time_flag[0])*60*60
            if 'DAY' in time_flag[1]:
                    timestamp = cur_time - int(time_flag[0])*24*60*60
        else:
            time_flag = time_flag.replace(',', '')
            time_flag = time_flag.split()
            d = datetime.date(int(time_flag[-1]),month[time_flag[0]], int(time_flag[1]))
            timestamp = time.mktime(d.timetuple())

        contents.append(title)
        update_times.append(timestamp)

    return (contents, update_times)



if __name__ == "__main__":
    # scrape_newsbitcoin(10,0)
    GetGoogleNews()
    # test()
    # print(re.search(r'ago', "AGO", flags=re.IGNORECASE))
    # getTweet()
    # cointele()
