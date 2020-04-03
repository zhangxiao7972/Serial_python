from PyQt5 import QtWidgets
import pyqtgraph as pg
import pandas as pd


class NowFileData(QtWidgets.QMainWindow):
    def __init__(self, title_str):
        super().__init__()
        self.setupUi()
        self.setWindowTitle(title_str)

    def setupUi(self):
        self.main_widget = QtWidgets.QWidget()  # 创建一个主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建一个网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置主部件的布局为网格
        self.setCentralWidget(self.main_widget)  # 设置窗口默认部件

        self.plot_widget = QtWidgets.QWidget()  # 实例化一个widget部件
        self.plot_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        self.plot_widget.setLayout(self.plot_layout)  # 设置K线图部件的布局层
        self.plot_plt = pg.PlotWidget()  # 实例化一个绘图部件
        self.plot_plt.showGrid(x=True, y=True)  # 显示图形网格
        self.plot_layout.addWidget(self.plot_plt)  # 添加绘图部件到K线图部件的网格布局层
        # 将上述部件添加到布局层中
        self.main_layout.addWidget(self.plot_widget, 1, 0, 3, 3)

        self.setCentralWidget(self.main_widget)
        # self.plot_plt.setYRange(max=100, min=0)
        self.data_list = []

    def drew(self, data):
        self.data_list.append(data)
        self.plot_plt.plot().setData(self.data_list, pen='g')


class GetFileData(QtWidgets.QMainWindow):
    def __init__(self, data, data_type):
        super().__init__()

        self.data_type = data_type
        # 各点纵坐标的值
        self.y = list(data[data_type])
        self.strs = list(data['Time'])
        self.x = range(len(self.y))
        # 定义每个x坐标值对应的字符列表
        # 其形式为：[(0, '2020-3-20'), (1, '2020-3-21'), (2, '2020-3-22')]
        self.ticks = [(i, self.strs[i][9:17]) for i in range(0, len(data.index), 5)]

        self.win = pg.GraphicsWindow(title=data_type)
        self.win.hide()
        self.plot = None
        self.vb = None
        self.proxy = None
        self.setupUi()
        self.init()

    def init(self):
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def setupUi(self):
        # 创建轴项类AxisItem的实例对象strAxis，并调用setTicks函数设置横坐标的字符信息
        self.str_axis = pg.AxisItem(orientation='bottom')
        self.str_axis.setTicks([self.ticks])

        self.plot = self.win.addPlot(axisItems={'bottom': self.str_axis}, title=self.data_type)
        self.plot.showGrid(x=True, y=True, alpha=0.5)
        # 添加label
        self.label = pg.TextItem()
        self.plot.addItem(self.label)
        # 画图
        self.plot.plot(self.x, self.y, pen='r', symbolBrush=(255, 0, 0))
        self.plot.setLabel(axis='left', text='观测值')
        self.plot.setLabel(axis='bottom', text='时间')
        # 设置十字光标
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)
        self.vb = self.plot.vb

    def mouseMoved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if 0 <= index < len(self.y):
                self.label.setText("日期：" + str(self.strs[index]) + '大小：' + str(self.y[index]))
                self.label.setPos(mousePoint.x(), mousePoint.y())
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
