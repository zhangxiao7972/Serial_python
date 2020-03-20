class Data_Deal(object):
    def __init__(self, data_str):
        self.target = data_str
        self.time = ""
        self.temp = 0
        self.humidity = 0
        self.speed = 0
        self.direction = 0
        self.pressure = 0

    def get_num(self):
        self.store_to_txt()
        self.time = ("20" + self.target[0:2] + "/" +
                     self.target[2:4] + "/" +
                     self.target[4:6] + "/ " +
                     self.target[6:8] + ":" +
                     self.target[8:10] + ":" +
                     self.target[10:12])
        self.temp = float(self.target[12:14] + "." + self.target[14:15])
        self.humidity = float(self.target[15:17] + "." + self.target[17:18])
        self.speed = float(self.target[18:20] + "." + self.target[20:21])

        self.direction = float(self.target[21:24] + "." + self.target[24:25])
        disp_direction = "xibei"

        self.pressure = float(self.target[25:29] + "." + self.target[29:30])

        return self.time, self.temp, self.humidity, self.speed, disp_direction, self.pressure

    def store_to_txt(self):
        file = open("Data.txt", "a")
        file.write(self.target+"\n")
        file.close()
