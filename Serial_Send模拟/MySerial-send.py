import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import datetime
import random


class Data_App(object):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial()
        self.timer = QTimer()

        # 串口接收的字符串
        self.send_data = None

        self.port_open()
        self.timer_start()

    def __del__(self):
        print("删除此对象！")
        self.port_close()

    # 启动定时器 时间间隔秒
    def timer_start(self):
        self.timer.timeout.connect(self.data_send)
        self.timer.start(1000)

    # 打开串口
    def port_open(self):
        self.ser.port = "COM2"
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = "N"
        try:
            print('打开串口中')
            self.ser.open()
        except:
            print("Com2串口打开失败！！")
            exit()
        if self.ser.isOpen():
            print('串口打开成功！')

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        try:
            self.ser.close()
        except:
            print("此串口未关闭成功！！")

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            self.get_str()
            # 非空字符串 ascii发送
            input_s = self.send_data.encode('utf-8')
            self.ser.write(input_s)

    # 获取要发送的字符串
    def get_str(self):
        # 获取当前时间
        now_time = datetime.datetime.now()
        time1_str = datetime.datetime.strftime(now_time, '%Y%m%d%H%M%S')

        temp = random.randint(5, 35)
        if temp < 10:
            temp_str = '0' + str(temp)
        else:
            temp_str = str(temp)
        # print(temp_str)

        hum = random.randint(5, 40)
        if hum < 10:
            hum_str = '0' + str(hum)
        else:
            hum_str = str(hum)
        # print(hum_str)
        speed = random.randint(2, 15)
        if speed < 10:
            speed_str = '0' + str(speed)
        else:
            speed_str = str(speed)
        # print(speed_str)
        dict = random.randint(0, 360)
        if dict < 10:
            dict_str = '00' + str(dict)
        elif 10 <= dict < 100:
            dict_str = '0' + str(dict)
        else:
            dict_str = str(dict)
        # print(dict_str)
        pressure = random.randint(990, 1010)
        if pressure < 1000:
            pressure_str = '0' + str(pressure)
        else:
            pressure_str = str(pressure)
        # print(pressure_str)
        a = str(random.randint(0, 9))

        self.send_data = time1_str[2:14] + temp_str + a + hum_str + a + \
                         speed_str + a + dict_str + a + pressure_str + a

        print(self.send_data)

    # 接收数据
    # def data_receive(self):
    #     try:
    #         num = self.ser.inWaiting()
    #     except:
    #         self.port_close()
    #         return None
    #
    #     if num > 0:
    #         # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
    #         # 200318444444253528132250310123
    #         self.receive_data = self.ser.read(num).decode('utf-8')
    #         self.data_operation()


if __name__ == "__main__":
    # file = open("Data.txt", "w")
    # file.write("以下为最新记录数据：\n")
    # file.close()

    app = QApplication(sys.argv)
    myshow = Data_App()
    sys.exit(app.exec_())
