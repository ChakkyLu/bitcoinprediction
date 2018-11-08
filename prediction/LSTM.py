import os
import numpy as np
import sys
sys.path.append("..")
from base.csv_operation import *
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.engine.saving import model_from_json
from keras.layers import LSTM, Dense, Activation
from keras.optimizers import Adam
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


class lstmModel():
    def __init__(self, TRAIN_TEST_RATIO=0.7, lr=0.006, hiden=200, in_out_neurons=1, time_step=20, epoch=100, model_path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/model/', data_path=os.path.abspath(os.path.join(os.getcwd(), ".."))+'/data/'):
        self.data_path = data_path
        self.ratio = TRAIN_TEST_RATIO
        self.n_hidden = hiden
        self.lr = lr
        self.in_out_neurons = in_out_neurons
        self.time_step = time_step
        self.epoch = epoch
        self.model_path = model_path
        self.model = None

    def getData(self, cur_price):
        assert not self.model
        cur_price = cur_price[::-1]
        cur_price = (cur_price - np.mean(self.data)) / np.std(self.data)
        cur_price = np.array(cur_price).reshape(1, self.time_step, 1)
        return cur_price

    def __prepare(self):
        filename = self.data_path + "bitcoin.csv"
        dicts = read_to_dict(filename)
        data = [float(i) for i in dicts.values()]
        self.data = data
        normalize_data = (data - np.mean(data)) / np.std(data)
        normalize_data = normalize_data[:, np.newaxis]
        trainx, trainy = [], []
        for i in range(len(normalize_data) - time_step - 1):
            x = normalize_data[i:i + time_step]
            y = normalize_data[i + time_step]
            trainx.append(x.tolist())
            trainy.append(y.tolist())
        trainx = trainx[len(trainx) - 10000:]
        trainy = trainy[len(trainy) - 10000:]
        trainx = np.array(trainx).reshape(len(trainx), time_step, 1)
        trainx = np.array(trainx).reshape(len(trainx), time_step, 1)
        trainy = np.array(trainy).reshape(len(trainy), 1)
        self.train_x = trainx[0:int(len(trainx) * self.ratio)]
        self.train_y = trainy[0:int(len(trainx) * self.ratio)]
        self.test_x = trainx[int(len(trainx) * self.ratio):]
        self.test_y = trainy[int(len(trainx) * self.ratio):]


    def train(self):
        print("===============Training Model===============")
        self.__prepare()
        model = Sequential()
        model.add(LSTM(self.n_hidden, batch_input_shape=(None, time_step, self.in_out_neurons)))
        model.add(Dense(self.in_out_neurons))
        model.add(Activation("linear"))
        optimizer = Adam(lr=self.lr)
        model.compile(loss="mean_squared_error", optimizer=optimizer)
        early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
        model.fit(self.train_x, self.train_y, batch_size=300, epochs=self.epoch, validation_split=0.1, callbacks=[early_stopping])
        model_json = model.to_json()
        with open(self.model_path+"lstm_model.json", "w") as json_file:
            json_file.write(model_json)
        model.save_weights("lstm_model.h5")
        self.model = model

    def predict(self, test_x):
        test_x = self.getData(test_x)
        if not self.model:
            json_file = open('lstm_model.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(loaded_model_json)
            self.model.load_weights("lstm_model.h5")
        predicted = self.model.predict(test_x)
        return predicted


    def model_analysis(self):
        max_error = [0.2, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02, 0.01]
        max_error = [0.08]
        if not self.model:
            json_file = open('lstm_model.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(loaded_model_json)
            self.model.load_weights("lstm_model.h5")
        predicted = self.model.predict(self.test_x)
        for error_rate in max_error:
            c = 0
            a = 0
            print("===========Bearness==========", error_rate)
            for i in range(len(predicted)):
                if (predicted[i] - self.test_y[i]) / self.test_y[i] < error_rate:
                    c += 1
                a += 1
            print("=====accuracy=====", str(c / a))
        # plt.figure()
        # plt.plot(predicted, color='r', label='predicted_data')
        # plt.plot(test_y, color='b', label='real_data')
        # plt.legend()
        # plt.show()
