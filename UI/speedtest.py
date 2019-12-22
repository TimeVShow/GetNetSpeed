#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from math import *
import sys, requests, time
burl = "http://172.104.57.94:8000/polls/"
#burl = "http://182.254.189.71:8000/polls/"
purl = burl + "post/"

proxy = '127.0.0.1:1080'
# 构造代理字典
proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy,
}


class PostThread(PyQt5.QtCore.QThread):
    '''继承于QThread，Post线程'''
    _signal = pyqtSignal(list)

    def __init__(self):
        super(PostThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        upspeed = []
        for i in range(0, 5):
            try:
                des = "download/" + str(0) + ".txt"
                try:
                    files = {'file': open(des, "rb")}
                    r = requests.post(purl,
                                      files=files,
                                      proxies=proxies,
                                      timeout=15)
                except:
                    files = {'file': open(des, "rb")}
                    r = requests.post(purl, files=files, timeout=15)
                try:
                    time = float(r.text)
                    print("now post netspeed is:%f MB/s\n" % ((1 << 0) / time))
                    upspeed.append((1 << 0) / time * 8)
                except:
                    print("Connection Error\n")
                    upspeed.append(0)
            except:
                print("Connection Error\n")
                upspeed.append(0)
        self._signal.emit(upspeed)


class GetThread(PyQt5.QtCore.QThread):
    '''继承于QThread，Get线程类'''
    _signal = pyqtSignal(list)

    def __init__(self):
        super(GetThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        #time.process_time()
        downspeed = []
        for i in range(0, 5):
            try:
                des = "download/" + str(0) + ".txt"
                before = time.perf_counter()
                durl = burl + str(0) + "/download/"
                try:
                    r = requests.get(durl, proxies=proxies, timeout=15)
                except:
                    r = requests.get(durl, timeout=15)
                after = time.perf_counter()
                if len(r.content) != 1024 * 1024:
                    downspeed.append(0)
                    print("Connection Error\n")
                    continue
                with open(des, "wb") as f:
                    f.write(r.content)
                print("now download netspeed is:%f MB/s\n" %
                      ((1 << 0) / (after - before)))
                downspeed.append((1 << 0) / (after - before) * 8)
            except:
                downspeed.append(0)
                print("Connection Error\n")
        self._signal.emit(downspeed)


class SpeedTestUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("speedtest")
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        self.resize(400, 600)  #画布布局

        self.setWindowOpacity(0.9)  #设置窗口透明度
        self.setAttribute(Qt.WA_TranslucentBackground)  #设置窗口背景透明
        self.setWindowFlag(Qt.FramelessWindowHint)  #隐藏边框

        self.downloadLabel = QLabel(self)  #用于显示下载gif和断网警告
        self.downloadLabel.setGeometry(QRect(340, 440, 50, 50))
        self.downloadLabel.setObjectName("downloadLabel")
        self.uploadLabel = QLabel(self)  #用于显示上传gif和断网警告
        self.uploadLabel.setGeometry(QRect(340, 515, 50, 50))
        self.uploadLabel.setObjectName("uploadLabel")
        self.loadingGif = QMovie('loading.gif')  #加载gif
        self.loadingGif.setScaledSize(QSize(50, 50))  #设置大小
        self.connectionErrorPix = QPixmap('error.jpg')  #断网警告

        #创建三个按钮:关闭、最大化、最小化
        self.pushButtonClose = QPushButton('×', self)
        self.pushButtonClose.setGeometry(QRect(367, 35, 24, 24))
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.pushButtonMaxi = QPushButton('□', self)
        self.pushButtonMaxi.setGeometry(QRect(327, 35, 24, 24))
        self.pushButtonMaxi.setObjectName("pushButtonMaxi")
        self.pushButtonMini = QPushButton('-', self)
        self.pushButtonMini.setGeometry(QRect(287, 35, 24, 24))
        self.pushButtonMini.setObjectName("pushButtonMini")
        self.pushButtonClose.setStyleSheet(
            "QPushButton{background:#F76677;border-radius:12px;}"
            "QPushButton:hover{background:red;}")
        self.pushButtonMaxi.setStyleSheet(
            "QPushButton{background:#F7D674;border-radius:12px;}"
            "QPushButton:hover{background:yellow;}")
        self.pushButtonMini.setStyleSheet(
            "QPushButton{background:#6DDF6D;border-radius:12px;}"
            "QPushButton:hover{background:green;}")
        #由于最大化可能会破坏布局，此处不给予最大化功能
        self.pushButtonClose.clicked.connect(self.close)  #关闭窗口
        self.pushButtonMini.clicked.connect(self.showMinimized)  #最小化窗口

        #创建开始测速按钮
        self.pushButtonStart = QPushButton('开始测速', self)
        self.pushButtonStart.setFont(QFont("华文琥珀", 18))
        self.pushButtonStart.setStyleSheet(
            "QPushButton{color:black}"
            "QPushButton:hover{color:purple}"
            "QPushButton{background-color:rgb(78,255,255)}"
            "QPushButton{border:2px}"
            "QPushButton{border-radius:10px}"
            "QPushButton{padding:2px 4px}")
        self.pushButtonStart.setMinimumWidth(100)
        self.pushButtonStart.setMinimumHeight(50)
        self.pushButtonStart.move(150, 50)
        self.pushButtonStart.clicked.connect(self.downloadStart)

        #窗口重绘定时器 此定时器用于更新显示
        self.systemTimer = QTimer()
        self.systemTimer.timeout.connect(self.update)  #绑定更新槽函数
        self.systemTimer.start(1)  #计时器每秒计数

        #测速演示定时器
        self.showTimer = QTimer()
        self.showTimer.timeout.connect(self.showTimerTimeoutHandle)

        self._startAngle = 135  #以QPainter坐标方向为准，0度为正右方，顺时针
        self._endAngle = 45  #以以QPainter坐标方向为准
        self._scaleMainNum = 8  #主刻度数
        self._minValue = 0  #最小数值
        self._maxValue = 300  #最大数值
        self._spdVal = [0, 5, 10, 15, 25, 50, 75, 150, 300]  #刻度盘数值
        self._showValue = 0  #当前演示数值
        self._nowValue = 0  #当前欲达数值
        self._downloadSpeed = []  #五次下载时间
        self._uploadSpeed = []  #五次上传时间
        self._count = 0  #当前演示的是第几次下载/上传数值
        self._AvgUploadSpeed = 0  #平均上传时间
        self._AvgDownloadSpeed = 0  #平均下载时间
        self._showObject = 1  #当前演示过程:下载(1) or 上传(0)
        self._showStop = 0  #演示结束为1

        #用来将QObject里的子孙QObject的某些信号按照其objectName连接到相应的槽上
        QMetaObject.connectSlotsByName(self)

    @pyqtSlot()
    def showTimerTimeoutHandle(self):
        '''演示下载/上传实时速度'''
        if self._showStop == 1:
            if int(10 * (self._showValue)) == 0:
                self._showValue = 0
                self.showTimer.stop()
                if self._showObject == 1:
                    self._showObject = 0
                    self.uploadStart()  #下载完后开始上传
        if self._count >= 4:
            self._count = 0
            if self._showObject == 0:
                self._AvgUploadSpeed = sum(self._uploadSpeed) / len(
                    self._uploadSpeed)
                self._nowValue = 0  #测速完后回降到0
                self._showStop = 1
                self.pushButtonStart.setEnabled(True)
            else:
                self._AvgDownloadSpeed = sum(self._downloadSpeed) / len(
                    self._downloadSpeed)
                self._nowValue = 0  #测速完后回降到0
                self._showStop = 1
        if int(10 * (self._showValue - self._nowValue)) != 0:
            #对数值的改变进行慢处理
            self._showValue = self._showValue + 0.07 * (
                1 if self._showValue < self._nowValue else -1)
        if int(10 * (self._showValue - self._nowValue)) == 0:
            if self._showStop == 1:
                return
            self._count += 1
            if self._showObject == 0:
                self._nowValue = self._uploadSpeed[self._count]
            else:
                self._nowValue = self._downloadSpeed[self._count]

    def downloadGifStart(self):
        self.downloadLabel.setMovie(self.loadingGif)
        self.loadingGif.start()

    def downloadGifStop(self):
        self.loadingGif.stop()
        self.downloadLabel.setMovie(None)

    def uploadGifStart(self):
        self.uploadLabel.setMovie(self.loadingGif)
        self.loadingGif.start()

    def uploadGifStop(self):
        self.loadingGif.stop()
        self.uploadLabel.setMovie(None)

    def mousePressEvent(self, event):
        '''鼠标点击事件'''
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  #获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  #更改鼠标图标为小手

    def mouseMoveEvent(self, QMouseEvent):
        '''鼠标点击后移动事件'''
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  #更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        '''鼠标点击后释放事件'''
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))  #更改鼠标图标为箭头

    def downloadStart(self):
        '''开启下载线程，避免界面卡住'''
        self.uploadLabel.setMovie(None)
        self.downloadLabel.setMovie(None)
        self.pushButtonStart.setEnabled(False)
        self.downloadGifStart()
        self._AvgUploadSpeed = 0
        self._AvgDownloadSpeed = 0
        # 创建线程
        self.thread = GetThread()
        # 连接信号
        self.thread._signal.connect(self.downloadShowStart)  #进程连接回传到GUI的事件
        # 开始线程
        self.thread.start()

    def downloadShowStart(self, msg):
        '''用进度条开始演示下载过程'''
        self.downloadGifStop()
        print(msg)
        if sum(msg) == 0:
            self.downloadLabel.setPixmap(self.connectionErrorPix)
            self.downloadLabel.setScaledContents(True)
        self._downloadSpeed = msg
        self._showObject = 1
        self._showStop = 0
        self.setShowTimer(True)

    def uploadStart(self):
        '''开启上传线程，避免界面卡住'''
        self.uploadGifStart()
        # 创建线程
        self.thread = PostThread()
        # 连接信号
        self.thread._signal.connect(self.uploadShowStart)  # 进程连接回传到GUI的事件
        # 开始线程
        self.thread.start()

    def uploadShowStart(self, msg):
        '''用进度条开始演示上传过程'''
        self.uploadGifStop()
        print(msg)
        if sum(msg) == 0:
            self.uploadLabel.setPixmap(self.connectionErrorPix)
            self.uploadLabel.setScaledContents(True)
        self._uploadSpeed = msg
        self._showStop = 0
        self._showObject = 0
        self.setShowTimer(True)

    def setShowTimer(self, flag):
        '''用进度条开始演示上传/下载过程'''
        if flag is True:
            self.showTimer.start(10)
        else:
            self.showTimer.stop()

    def paintEvent(self, event):
        '''在self.systemTimer触发的self.update下进行更新画面'''
        side = min(self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        #painter坐标系原点移至widget中央
        painter.scale(side / 220, side / 220)
        #缩放painterwidget坐标系，使绘制的表盘位于widge中央,即表盘支持缩放

        self.drawPanel(painter)  #画外框表盘
        self.drawScaleNum(painter)  #画刻度数字
        self.drawIndicator(painter)  #画指针
        self.drawWords(painter)  #画文字
        self.drawValues(painter)  #画数值

    def drawPanel(self, p):
        '''画外框表盘'''
        p.save()
        '''画黑色圆角矩形背景'''
        p.setBrush(Qt.black)
        p.drawRoundedRect(QRect(-110, -150, 220, 300), 10, 10, Qt.RelativeSize)
        '''画表盘'''
        sliptScale = (360 - (self._startAngle - self._endAngle)) / 8
        for i in range(len(self._spdVal)):
            if self._showValue < self._spdVal[i]:
                break
        degRotate = sliptScale * (i - 1) + (self._showValue - self._spdVal[
            i - 1]) / (self._spdVal[i] - self._spdVal[i - 1]) * sliptScale
        radius = 100
        #画小于self._showValue的进度条部分扇形
        lg = QLinearGradient(-radius, -radius, radius, radius)
        lg.setColorAt(abs(self._showObject - 1), QColor(0, 213, 243))
        lg.setColorAt(self._showObject, QColor(0, 229, 198))  #外框渐变颜色
        p.setBrush(lg)
        p.setPen(Qt.NoPen)
        p.drawPie(-radius, -radius, radius * 2, radius * 2,
                  (225 - degRotate) * 16, degRotate * 16)
        #画大于self._showValue的进度条部分扇形
        p.setBrush(QColor(88, 93, 114))
        p.drawPie(-radius, -radius, radius * 2, radius * 2, -45 * 16,
                  (270 - degRotate) * 16)
        #画一个略小的黑色扇形
        p.setBrush(Qt.black)
        p.drawPie(-radius + 12, -radius + 12, (radius - 12) * 2,
                  (radius - 12) * 2, -40 * 16, 260 * 16)
        #画一个圆形与上面重叠显示出棱角
        p.setBrush(Qt.black)
        p.drawEllipse(-83, -83, 83 * 2, 83 * 2)
        p.restore()

    def drawScaleNum(self, p):
        p.save()
        startRad = self._startAngle * (3.14 / 180)
        stepRad = (360 - (self._startAngle - self._endAngle)) * (
            3.14 / 180) / self._scaleMainNum
        p.setFont(QFont('Times New Roman', 10))
        fm = QFontMetricsF(p.font())
        for i in range(0, self._scaleMainNum + 1):
            sina = sin(startRad + i * stepRad)
            cosa = cos(startRad + i * stepRad)
            s = str(self._spdVal[i])
            if self._showValue > int(s):
                p.setPen(QColor(0, 213, 243))
            else:
                p.setPen(QColor(88, 93, 114))
            w = fm.size(Qt.TextSingleLine, s).width()
            h = fm.size(Qt.TextSingleLine, s).height()
            x = 74 * cosa - w / 2
            y = 74 * sina - h / 2
            p.drawText(QRectF(x, y, w, h), s)

        p.restore()

    def drawIndicator(self, p):
        '''画指针'''
        p.save()
        polygon = QPolygon(
            [QPoint(0, -6),
             QPoint(0, 6),
             QPoint(60, 5),
             QPoint(60, -5)])
        sliptScale = (360 - (self._startAngle - self._endAngle)) / 8
        for i in range(len(self._spdVal)):
            if self._showValue < self._spdVal[i]:
                break
        degRotate = self._startAngle + sliptScale * (i - 1) + (
            self._showValue - self._spdVal[i - 1]) / (
                self._spdVal[i] - self._spdVal[i - 1]) * sliptScale
        #画指针
        p.rotate(degRotate)
        halogd = QRadialGradient(0, 0, 60, 0, 0)
        halogd.setColorAt(1, QColor(244, 244, 244))
        halogd.setColorAt(0, QColor(0, 0, 0))
        p.setBrush(halogd)
        p.drawConvexPolygon(polygon)
        p.restore()

    def drawWords(self, p):
        '''画文字'''
        p.save()
        p.setPen(Qt.white)
        p.setFont(QFont('Times New Roman', 18))  #给画布设置字体、大小
        p.drawText(-27, 60, 'Mbps')
        p.setFont(QFont('Times New Roman', 18))  #给画布设置字体、大小
        p.drawText(-75, 140, 'upload:')
        p.setFont(QFont('Times New Roman', 18))  #给画布设置字体、大小
        p.drawText(-105, 100, 'download:')
        p.restore()

    def drawValues(self, p):
        '''画数值'''
        p.save()
        '''画实时数值'''
        p.setPen(Qt.white)
        p.setFont(QFont('Times New Roman', 24))  #给画家设置字体、大小
        #画整数部分
        s = str(int(self._showValue))
        fm = QFontMetricsF(p.font())
        w1 = fm.size(Qt.TextSingleLine, s).width()
        h1 = fm.size(Qt.TextSingleLine, s).height()
        x1 = -w1
        y1 = -h1 / 2
        p.drawText(QRectF(x1, y1 + 5, w1, h1), s)
        #画小数部分
        s1 = int(100 * (self._showValue - int(self._showValue)))
        s = '.' + str(s1) if s1 >= 10 else '.0' + str(s1)
        p.setFont(QFont('Times New Roman', 18))
        fm = QFontMetricsF(p.font())
        w2 = fm.size(Qt.TextSingleLine, s).width()
        h2 = fm.size(Qt.TextSingleLine, s).height()
        x2 = 0
        y2 = -h1 / 2 + (h1 - h2)
        p.drawText(QRectF(x2, y2 - 2 + 5, w2, h2), s)
        '''画上传数值'''
        p.setPen(QColor(0, 213, 243))
        p.setFont(QFont('Times New Roman', 24))  #给画家设置字体、大小
        #画整数部分
        s = str(int(self._AvgUploadSpeed))
        fm = QFontMetricsF(p.font())
        w1 = fm.size(Qt.TextSingleLine, s).width()
        h1 = fm.size(Qt.TextSingleLine, s).height()
        x1 = -w1
        y1 = -h1 / 2
        p.drawText(QRectF(x1 + 40, y1 + 130, w1, h1), s)
        #画小数部分
        s1 = int(100 * (self._AvgUploadSpeed - int(self._AvgUploadSpeed)))
        s = '.' + str(s1) if s1 >= 10 else '.0' + str(s1)
        p.setFont(QFont('Times New Roman', 18))
        fm = QFontMetricsF(p.font())
        w2 = fm.size(Qt.TextSingleLine, s).width()
        h2 = fm.size(Qt.TextSingleLine, s).height()
        x2 = 0
        y2 = -h1 / 2 + (h1 - h2)
        p.drawText(QRectF(x2 + 40, y2 - 2 + 130, w2, h2), s)
        '''画下载数值'''
        p.setPen(QColor(0, 229, 198))
        p.setFont(QFont('Times New Roman', 24))
        #画整数部分
        s = str(int(self._AvgDownloadSpeed))
        fm = QFontMetricsF(p.font())
        w1 = fm.size(Qt.TextSingleLine, s).width()
        h1 = fm.size(Qt.TextSingleLine, s).height()
        x1 = -w1
        y1 = -h1 / 2
        p.drawText(QRectF(x1 + 40, y1 + 90, w1, h1), s)
        #画小数部分
        s1 = int(100 * (self._AvgDownloadSpeed - int(self._AvgDownloadSpeed)))
        s = '.' + str(s1) if s1 >= 10 else '.0' + str(s1)
        p.setFont(QFont('Times New Roman', 18))
        fm = QFontMetricsF(p.font())
        w2 = fm.size(Qt.TextSingleLine, s).width()
        h2 = fm.size(Qt.TextSingleLine, s).height()
        x2 = 0
        y2 = -h1 / 2 + (h1 - h2)
        p.drawText(QRectF(x2 + 40, y2 - 2 + 90, w2, h2), s)
        p.restore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gp = SpeedTestUI()
    gp.show()
    app.exec_()
