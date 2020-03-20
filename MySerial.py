import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox
from PyQt5.QtCore import QTimer
from MyMainWindow import Ui_MainWindow
from data_deal import Data_Deal


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

        # 串口接收的字符串
        self.receive_data = None
        # 接收数据处理后的元组
        self.display_value = ()

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
        # 获取文件按钮 检测
        self.Button_Getfile.clicked.connect(self.data_send)
        # 串口检测按钮
        self.Button_FindPort.clicked.connect(self.port_check)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        port_list = None
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
        self.ser.port = "COM10"
        # self.ser.port = self.Box_get_port.currentText()
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
            # 打开串口接收定时器，周期为2ms
            self.timer.start(2)
            self.Button_Open.setText("关闭")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        try:
            self.ser.close()
        except:
            pass

        if ~self.ser.isOpen():
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
            self.receive_data = self.ser.read(num).decode('utf-8')
            self.data_operation()

    # 清除显示
    def receive_data_clear(self):
        self.textBrowser.setText("")

    # 处理接收的数据
    def data_operation(self):
        if len(self.receive_data) == 30:
            # 创建一个数据对象
            data = Data_Deal(self.receive_data)
            self.display_value = data.get_num()
            self.show_update()

        else:
            self.textBrowser.insertPlainText("Data Receive Error: Wrong Data Length!\r\n")

    def show_update(self):
        self.textBrowser.insertPlainText(self.receive_data + "\r\n")
        self.label_time.setText(self.display_value[0])
        self.label_temp.setText(str(self.display_value[1]))
        self.label_humidity.setText(str(self.display_value[2]))
        self.label_speed.setText(str(self.display_value[3]))
        self.label_dierction.setText(str(self.display_value[4]))
        self.label_pressure.setText(str(self.display_value[5]))

        # 对textBrowser中的操作：获取到text光标
        textCursor = self.textBrowser.textCursor()
        # 滚动到底部
        textCursor.movePosition(textCursor.End)
        # 设置光标到text中去
        self.textBrowser.setTextCursor(textCursor)


if __name__ == "__main__":
    file = open("Data.txt", "w")
    file.write("以下为最新记录数据：\n")
    file.close()

    app = QApplication(sys.argv)
    myshow = Data_App()
    myshow.main_window.show()
    sys.exit(app.exec_())
