import os

import numpy as np
import sys
sys.path.append("..")
from base.csv_operation import *
from base.price_grabber import *
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.engine.saving import model_from_json
from keras.layers import LSTM, Dense, Activation
from keras.optimizers import Adam
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import time

def getData(filename):
    dicts = read_to_dict(filename)
    prices = [float(i) for i in dicts.values()]
    return prices

flag = 1
path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/'
model_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/model/'

if flag:
    data = getData(path+"bitcoin_price.csv")
    normalize_data=(data-np.mean(data))/np.std(data)
    # cur_pre = getData(('previous_price.csv'))
    # cur_pre = cur_pre[::-1]
    # cur_pre = (cur_pre - np.mean(data))/np.std(data)

    normalize_data=normalize_data[:, np.newaxis]

    trainx,trainy=[],[]
    time_step=20
    train_test_ratio = 0.7
    for i in range(len(normalize_data)-time_step-1):
        x=normalize_data[i:i+time_step]
        y=normalize_data[i+time_step]
        trainx.append(x.tolist())
        trainy.append(y.tolist())
    # trainx = trainx[len(trainx)-10000:]
    # trainy = trainy[len(trainy)-10000:]
    trainx = np.array(trainx).reshape(len(trainx), time_step, 1)
    trainx = np.array(trainx).reshape(len(trainx), time_step, 1)
    trainy = np.array(trainy).reshape(len(trainy), 1)
    train_x = trainx[0:int(len(trainx)*train_test_ratio)]
    train_y = trainy[0:int(len(trainx)*train_test_ratio)]
    test_x = trainx[int(len(trainx)*train_test_ratio):]
    test_y = trainy[int(len(trainx)*train_test_ratio):]
    # cur_pre = np.array(cur_pre).reshape(1, time_step, 1)

def lstm():
    in_out_neurons = 1
    n_hidden = 200

    model = Sequential()
    model.add(LSTM(n_hidden, batch_input_shape=(None, time_step, in_out_neurons)))
    model.add(Dense(in_out_neurons))
    model.add(Activation("linear"))
    optimizer = Adam(lr=0.006)
    model.compile(loss="mean_squared_error", optimizer=optimizer)

    early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
    model.fit(train_x, train_y, batch_size=300, epochs=5, validation_split=0.1, callbacks=[early_stopping])
    model_json = model.to_json()
    with open(path+"lstm_model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights(path+"lstm_model.h5")
    print("=====Saved model Ok======")

    # predicted = model.predict(test_x)

    # plt.figure()
    # plt.plot(predicted, color='r', label='predicted_data')
    # plt.plot(test_y, color='b', label='real_data')
    # plt.legend()
    # plt.show()

def up_down_test():
    json_file = open(model_path + 'lstm_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(model_path+"lstm_model.h5")
    print("=======Loaded model ok========")
    predicted = model.predict(test_x)


    print("===========test==========")
    # max_error = [0.2, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02, 0.01]
    max_error = [0.08]
    for error_rate in max_error:
        c = 0
        a = 0
        print("===========test==========",error_rate)
        for i in range(len(predicted)):
            if (predicted[i] - test_y[i])/test_y[i] < error_rate:
                c += 1
            a += 1
        print("=====accuracy=====",str(c/a))
    fig = plt.figure()
    plt.plot(predicted[0:100], color='r', label='predicted_data')
    plt.plot(test_y[0:100], color='b', label='real_data')
    plt.legend()
    plt.show()
    fig.savefig('temp.png')

def test_lstm(x):
    json_file = open('lstm_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights("lstm_model.h5")
    print("=======Loaded model ok========")
    predicted = model.predict(x)
    print("=====predict as======", predicted)
    print("=====previous =======", x[-1][-1])


def getBitcoin():
    btc_chart_data = get_poloniex_data('USDT_BTC', 300, 1506816000)
    btc_chart_data.set_index('date', inplace=True)
    start_time = 1506816000
    step_time = 300
    price_and_time = {}
    while start_time < int(time.time()):
        price = btc_chart_data.iloc[
            btc_chart_data.index.get_loc(start_time, method='nearest')]['close']
        price_and_time[start_time] = price
        start_time += step_time
    print("======write the price======")
    write_to_csv(price_and_time, path+"bitcoin_price.csv", ['date', 'price'])
