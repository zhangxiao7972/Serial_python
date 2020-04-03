# encoding: utf-8
import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QWidget, QMessageBox
from PyQt5.QtCore import QTimer
from Drew import NowFileData, GetFileData
import pandas as pd
from MyMainWindow import Ui_MainWindow
from Data_Deal import Data_Deal


class Data_App(QWidget, Ui_MainWindow):
    def __init__(self):
        super(Data_App, self).__init__()
        self.ser = serial.Serial()
        self.timer = QTimer()
        self.main_window = QMainWindow()
        self.setupUi(self.main_window)
        self.retranslateUi(self.main_window)

        # 储存所有存在的串口 字典
        self.Com_Dict = {}
        # 串口开关标志
        self.open_flag = False
        # 创建新csv文件标志
        self.create_file_flag = True
        # 要保存的当前的文件名
        self.now_file_name = None
        # 串口接收的字符串
        self.receive_data = None
        # 绘图数据来源 标志位： True为当前数据 False为选择文件
        self.source_file_flag = True
        # 要画图的 选择的文件名
        self.get_fileName = None
        self.get_file_data = None
        # 接收数据处理后的元组
        self.display_value = ()
        # 创建四个要素图像对象
        self.temp_chart = None
        self.humidity_chart = None
        self.speed_chart = None
        self.direction_chart = None
        self.pressure_chart = None
        self.create_now_chart()

        self.init()
        self.port_check()

    # 按键关联
    def init(self):
        # 串口开关按钮 检测
        self.Button_Open.clicked.connect(self.port_opreation)
        # 定时器接收数据
        self.timer.timeout.connect(self.data_receive)
        # 清空接收区
        self.Button_Clear.clicked.connect(self.receive_data_clear)
        self.Button_exit.clicked.connect(self.app_close)
        # 获取文件按钮 检测
        self.Button_Getfile.clicked.connect(self.data_send)
        # 串口检测按钮
        self.Button_FindPort.clicked.connect(self.port_check)
        # 显示图像 关联信号和槽
        self.display_Temp.triggered.connect(self.show_temp_chart)
        self.display_Humidity.triggered.connect(self.show_humi_chart)
        self.display_speed.triggered.connect(self.show_speed_chart)
        self.display_Direction.triggered.connect(self.show_direction_chart)
        self.display_Pressure.triggered.connect(self.show_pressure_chart)
        # 菜单 选择当前文件绘图 还是选择另外的文件绘图
        self.get_file_drew.triggered.connect(self.data_source_get)
        self.now_file_drew.triggered.connect(self.data_source_now)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        port_list = list(serial.tools.list_ports.comports())
        self.Box_get_port.clear()
        if len(port_list) == 0:
            self.Box_get_port.addItem("无串口")
            QMessageBox.information(self, "信息", "未检测到串口！")
        else:
            self.Box_get_port.clear()
            for port in port_list:
                self.Com_Dict["%s" % port[0]] = "%s" % port[1]
                self.Box_get_port.addItem(port[0])

    # 串口开关操作
    def port_opreation(self):
        self.open_flag = ~self.open_flag
        if self.open_flag:
            self.port_open()
        else:
            self.port_close()

    # 打开串口
    def port_open(self):
        self.ser.port = self.Box_get_port.currentText()
        self.ser.baudrate = 115200
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = "N"

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        if self.ser.isOpen():
            # 打开串口接收定时器，周期为100ms
            self.timer.start(100)
            self.Button_Open.setText("关闭")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        try:
            self.ser.close()
        except:
            pass

        if not self.ser.isOpen():
            self.Button_Open.setText("打开")

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = "Get"
            # 非空字符串 ascii发送
            input_s = (input_s + '\r\n').encode('utf-8')
            self.ser.write(input_s)
        else:
            QMessageBox.critical(self, "Send Error", "未打开串口！")

    # 接收数据
    def data_receive(self):

        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None

        if num > 0:
            # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
            # 200318444444253528132250310123
            self.receive_data = self.ser.read(num).decode('utf-8')
            self.data_operation()

    # 清除显示
    def receive_data_clear(self):
        self.textBrowser.setText("")

    # 处理接收的数据
    def data_operation(self):
        if len(self.receive_data) == 30:
            # 创建一个数据对象，来处理数据
            data = Data_Deal(self.receive_data)
            # 解码并获得返回值，以便后面更新显示
            self.display_value = data.get_num()
            # 判断需要创建一个新的csv还是直接存入当前csv
            if self.create_file_flag:
                self.create_file_flag = False
                self.now_file_name = self.receive_data[4:6] + "_" + \
                                     self.receive_data[6:8] + "_" + \
                                     self.receive_data[8:10] + ".csv"
                data.create_csv(self.now_file_name)
            else:
                data.store_to_csv(self.now_file_name)
            self.show_update()

        else:
            self.textBrowser.insertPlainText("Data Receive Error: Wrong Data Length!\r\n")

    # 更新所有显示
    def show_update(self):
        self.textBrowser.insertPlainText(self.receive_data + "\r\n")
        self.label_time.setText(self.display_value[0])
        self.label_temp.setText(str(self.display_value[1]))
        self.label_humidity.setText(str(self.display_value[2]))
        self.label_speed.setText(str(self.display_value[3]))
        self.label_dierction.setText(str(self.display_value[5]))
        self.label_pressure.setText(str(self.display_value[6]))

        if self.source_file_flag:
            self.statusBar.showMessage("绘图对象：实时数据，当前文件为 %s" % self.now_file_name)
            self.temp_chart.drew(self.display_value[1],self.display_value[0][-5:])
            self.humidity_chart.drew(self.display_value[2],self.display_value[0][-5:])
            self.speed_chart.drew(self.display_value[3],self.display_value[0][-5:])
            self.direction_chart.drew(self.display_value[4],self.display_value[0][-5:])
            self.pressure_chart.drew(self.display_value[6],self.display_value[0][-5:])
        else:
            self.statusBar.showMessage("绘图对象：选择的文件数据，选择的文件为  %s" % self.get_fileName[0][-12:])

        # 对textBrowser中的操作：获取到text光标
        textCursor = self.textBrowser.textCursor()
        # 滚动到底部
        textCursor.movePosition(textCursor.End)
        # 设置光标到text中去
        self.textBrowser.setTextCursor(textCursor)

    # 菜单栏点击了 实时数据绘图
    def data_source_now(self):
        # 如果self.source_file_flag 本来就是True，则不作处理
        if self.source_file_flag:
            if not self.now_file_name:
                QMessageBox.critical(self, "Error", "此刻没有实时数据，不能绘图！")
        else:
            if not self.now_file_name or not self.ser.isOpen():
                QMessageBox.critical(self, "Error", "此刻没有实时数据，不能绘图！")
                self.statusBar.showMessage('绘图对象：实时数据。此刻没有实时数据，不能绘图！')
            else:
                self.source_file_flag = True
                self.statusBar.showMessage("绘图对象：实时数据，当前文件为 %s" % self.now_file_name)
                self.create_now_chart()

    # 菜单栏点击了 选择文件绘图
    def data_source_get(self):
        # 获取文件名
        self.get_fileName = QFileDialog.getOpenFileName(self, "选择文件", ".", "All Files (*.csv)")
        self.get_file_data = pd.read_csv(self.get_fileName[0])
        self.source_file_flag = False
        self.statusBar.showMessage("绘图对象：选择的文件数据，选择的文件为  %s" % self.get_fileName[0][-12:])
        self.create_get_chart()

    # 创建实时数据图像对象
    def create_now_chart(self):
        self.temp_chart = NowFileData("温度")
        # 设置纵坐标大小
        self.temp_chart.plot.setYRange(max=50, min=0)
        self.humidity_chart = NowFileData("湿度")
        self.humidity_chart.plot.setYRange(max=100, min=0)
        self.speed_chart = NowFileData("风速")
        self.speed_chart.plot.setYRange(max=20, min=0)
        self.direction_chart = NowFileData("风向")
        self.pressure_chart = NowFileData("大气压")
        self.pressure_chart.plot.setYRange(max=1050, min=950)
        # 当前显示的窗口
        self.chart_flag = 1
        self.chart_dictionary = {1: self.temp_chart,
                                 2: self.humidity_chart,
                                 3: self.speed_chart,
                                 4: self.direction_chart,
                                 5: self.pressure_chart}

    # 创建实时数据图像对象
    def create_get_chart(self):
        self.temp_chart = GetFileData(self.get_file_data, 'Temperature')
        self.temp_chart.plot.setYRange(max=50, min=0)
        self.humidity_chart = GetFileData(self.get_file_data, 'Humidity')
        self.humidity_chart.plot.setYRange(max=100, min=0)
        self.speed_chart = GetFileData(self.get_file_data, 'Speed')
        self.speed_chart.plot.setYRange(max=20, min=0)
        self.direction_chart = None
        self.pressure_chart = GetFileData(self.get_file_data, 'Pressure')
        self.pressure_chart.plot.setYRange(max=1050, min=950)
        # 当前显示的窗口
        self.chart_flag = 1
        self.chart_dictionary = {1: self.temp_chart,
                                 2: self.humidity_chart,
                                 3: self.speed_chart,
                                 4: self.direction_chart,
                                 5: self.pressure_chart}

    # 绘制温度图像
    def show_temp_chart(self):
        if self.source_file_flag and not self.now_file_name:
            QMessageBox.critical(self, "Show Error", "此刻没有接收数据！")
            return
        # 获取坐标：前一个图标的坐标
        new_point = self.chart_dictionary[self.chart_flag].win.geometry()
        # 将上一个图像隐藏
        self.chart_dictionary[self.chart_flag].win.hide()
        # 设置这个图像的坐标
        self.temp_chart.win.setGeometry(new_point)
        # 显示这个图像
        self.temp_chart.win.show()
        # 更换标志位
        self.chart_flag = 1

    # 绘制湿度图像
    def show_humi_chart(self):
        if self.source_file_flag and not self.now_file_name:
            QMessageBox.critical(self, "Show Error", "此刻没有接收数据！")
            return
        new_point = self.chart_dictionary[self.chart_flag].win.geometry()
        self.chart_dictionary[self.chart_flag].win.hide()
        self.humidity_chart.win.setGeometry(new_point)
        self.humidity_chart.win.show()
        self.chart_flag = 2

    # 绘制风速图像
    def show_speed_chart(self):
        if self.source_file_flag and not self.now_file_name:
            QMessageBox.critical(self, "Show Error", "此刻没有接收数据！")
            return
        new_point = self.chart_dictionary[self.chart_flag].win.geometry()
        self.chart_dictionary[self.chart_flag].win.hide()
        self.speed_chart.win.setGeometry(new_point)
        self.speed_chart.win.show()
        self.chart_flag = 3

    # 绘制大气压图像
    def show_pressure_chart(self):
        if self.source_file_flag and not self.now_file_name:
            QMessageBox.critical(self, "Show Error", "此刻没有接收数据！")
            return
        new_point = self.chart_dictionary[self.chart_flag].win.geometry()
        self.chart_dictionary[self.chart_flag].win.hide()
        self.pressure_chart.win.setGeometry(new_point)
        self.pressure_chart.win.show()
        self.chart_flag = 5

    # 绘制风向图像
    def show_direction_chart(self):
        if self.source_file_flag:
            if self.now_file_name:
                new_point = self.chart_dictionary[self.chart_flag].win.geometry()
                self.chart_dictionary[self.chart_flag].win.hide()
                self.direction_chart.win.setGeometry(new_point)
                self.direction_chart.win.show()
            else:
                QMessageBox.critical(self, "Show Error", "此刻没有接收数据！")
            self.chart_flag = 4
        else:
            QMessageBox.information(self, "信息", "非实时数据，不能绘制风向变化图像！")

    # 关闭系统
    def app_close(self):
        self.port_close()
        quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = Data_App()
    myshow.main_window.show()
    sys.exit(app.exec_())
