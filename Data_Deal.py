import pandas as pd
import numpy as np


class Data_Deal(object):
    def __init__(self, data_str):
        self.target = data_str
        self.time = ""
        self.temp = 0
        self.humidity = 0
        self.speed = 0
        self.direction = 0
        self.pressure = 0
        self.disp_direction = []

    # 解码各气象要素，便于显示和绘图
    def get_num(self):
        self.time = ("20" + self.target[0:2] + "/" +
                     self.target[2:4] + "/" +
                     self.target[4:6] + " " +
                     self.target[6:8] + ":" +
                     self.target[8:10] + ":" +
                     self.target[10:12])
        self.temp = float(self.target[12:14] + "." + self.target[14:15])
        self.humidity = float(self.target[15:17] + "." + self.target[17:18])
        self.speed = float(self.target[18:20] + "." + self.target[20:21])

        self.direction = float(self.target[21:24] + "." + self.target[24:25])
        self.disp_direction = self.direction_decode()

        self.pressure = float(self.target[25:29] + "." + self.target[29:30])

        return self.time, self.temp, self.humidity, self.speed, \
               self.disp_direction[0], self.disp_direction[1], self.pressure

    # 风向解码
    def direction_decode(self):
        if self.direction > 348.76 or self.direction < 11.25:
            stdander_dir = 0
            dir_str = "北"
            store_str = 'N'
        elif 11.26 < self.direction < 33.75:
            stdander_dir = 22.5
            dir_str = "北东北"
            store_str = 'NEN'
        elif 33.76 < self.direction < 56.25:
            stdander_dir = 45
            dir_str = "东北"
            store_str = 'EN'
        elif 56.26 < self.direction < 78.75:
            stdander_dir = 67.5
            dir_str = "东东北"
            store_str = 'EEN'
        elif 78.76 < self.direction < 101.25:
            stdander_dir = 90
            dir_str = "东"
            store_str = 'E'
        elif 101.26 < self.direction < 123.75:
            stdander_dir = 112.5
            dir_str = "东东南"
            store_str = 'EES'
        elif 123.76 < self.direction < 146.25:
            stdander_dir = 135
            dir_str = "东南"
            store_str = 'ES'
        elif 146.26 < self.direction < 168.75:
            stdander_dir = 157.5
            dir_str = "南东南"
            store_str = 'SES'
        elif 168.76 < self.direction < 191.25:
            stdander_dir = 180
            dir_str = "南"
            store_str = 'S'
        elif 191.26 < self.direction < 213.75:
            stdander_dir = 202.5
            dir_str = "南西南"
            store_str = 'SWS'
        elif 213.76 < self.direction < 236.25:
            stdander_dir = 225
            dir_str = "西南"
            store_str = 'WS'
        elif 236.26 < self.direction < 258.75:
            stdander_dir = 247.5
            dir_str = "西西南"
            store_str = 'WWS'
        elif 258.76 < self.direction < 281.25:
            stdander_dir = 270
            dir_str = "西"
            store_str = 'W'
        elif 281.76 < self.direction < 303.75:
            stdander_dir = 295.5
            dir_str = "西西北"
            store_str = 'WWN'
        elif 303.76 < self.direction < 326.25:
            stdander_dir = 315
            dir_str = "西北"
            store_str = 'WN'
        elif 326.26 < self.direction < 348.75:
            stdander_dir = 337.5
            dir_str = "北西北"
            store_str = 'NWN'

        return stdander_dir, dir_str, store_str

    def store_to_txt(self):
        file = open("Data.txt", "a")
        file.write(self.target + "\n")
        file.close()

    def create_csv(self, file_name):
        df = pd.DataFrame({'Time': self.time[2:],
                           'Temperature': [self.temp],
                           'Humidity': self.humidity,
                           'Speed': self.speed,
                           'Direc_num': self.disp_direction[0],
                           'Direc_str': self.disp_direction[2],
                           'Pressure': self.pressure})
        df.to_csv(file_name, index=False)

    def store_to_csv(self, file_name):
        data_buff = pd.DataFrame({'Time': self.time[2:],
                                  'Temperature': self.temp,
                                  'Humidity': self.humidity,
                                  'Speed': self.speed,
                                  'Direc_num': self.disp_direction[0],
                                  'Direc_str': self.disp_direction[2],
                                  'Pressure': self.pressure}, index=[1])
        data_buff.to_csv(file_name, mode='a', encoding='utf-8',
                         header=False, index=False)
