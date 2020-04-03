from PyQt5 import QtWidgets, QtGui
import pyqtgraph as pg


class NowFileData(QtWidgets.QMainWindow):
    def __init__(self, title_str):
        super().__init__()
        self.title_str = title_str
        self.win = pg.GraphicsWindow(title=title_str)
        self.win.hide()
        # 存储 y 坐标
        self.y = []
        # 存储点的横坐标的index
        self.x = []
        self.plot = None
        # 存储坐标轴
        # 定义每个x坐标值对应的字符列表
        # 其形式为：[(0, '2020-3-20'), (1, '2020-3-21'), (2, '2020-3-22')]
        self.ticks = []
        # 记录点的数量
        self.count = 0

        self.setupUi()

    def setupUi(self):
        # 创建轴项类AxisItem的实例对象strAxis，并调用setTicks函数设置横坐标的字符信息
        self.str_axis = pg.AxisItem(orientation='bottom')
        self.str_axis.setTicks([self.ticks])

        self.plot = self.win.addPlot(axisItems={'bottom': self.str_axis}, title=self.title_str)
        self.plot.showGrid(x=True, y=True, alpha=0.5)

        self.plot.setLabel(axis='left', text='观测值')
        self.plot.setLabel(axis='bottom', text='日期')

    def drew(self, data, time_str):
        self.ticks.append((self.count, time_str))
        if 20 < self.count < 60:
            show_ticks = self.ticks[0:self.count:5]
        else:
            show_ticks = self.ticks[0:self.count:10]
        self.str_axis.setTicks([show_ticks])
        self.count += 1
        self.x = range(self.count)
        self.y.append(data)
        # 画图
        self.plot.plot(self.x, self.y, pen='r', symbolBrush=(255, 0, 0))


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
        len_y = len(self.y)
        if len_y < 60:
            self.ticks = [(i, self.strs[i][9:17]) for i in range(0, len(data.index), 5)]
        elif len_y < 200:
            self.ticks = [(i, self.strs[i][9:17]) for i in range(0, len(data.index), 10)]
        else:
            self.ticks = [(i, self.strs[i][9:17]) for i in range(0, len(data.index), 30)]

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
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label.setFont(font)
        self.plot.addItem(self.label)
        # 画图
        self.plot.plot(self.x, self.y, pen='g', symbolBrush=(255, 0, 0))
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
                self.label.setHtml("<p style='color:white'>时间：{0}</p>"
                                   "<p style='color:white'>观测值：{1}</p>"
                              .format(self.strs[index], str(self.y[index])))
                self.label.setPos(mousePoint.x(), mousePoint.y())
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
