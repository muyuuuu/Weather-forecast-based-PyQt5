#!/bin/bash
# -*- coding: UTF-8 -*-
# 基本控件都在这里面
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget,
                            QGridLayout, QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                            QSlider, QLabel, QLineEdit, QPushButton, QTableWidget)
from PyQt5.QtGui import QPalette, QColor, QBrush
from PyQt5.QtCore import Qt
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg 
import numpy as np
import pyqtgraph.exporters as pe
import qdarkstyle, requests, sys, time, random, json, read_citycode, get_weather, datetime, re


class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        pg.setConfigOption('background', '#19232D')
        pg.setConfigOption('foreground', 'd')
        pg.setConfigOptions(antialias = True)
        
        # 窗口居中显示
        self.center()

        self.init_ui()
        # 设置城市的编号
        self.code = ""

        # 多次查询时，查询近5天， 受限于 API 接口提供的数量
        self.num = 5
        
        # return request json file
        self.rep = ""

        # 创建绘图面板
        self.plt = []
        # 控制绘图的文件名称
        self.filename = 1
        # 默认的状态栏
        # 可以设置其他按钮点击 参考多行文本显示 然而不行 
        self.status = self.statusBar()
        self.status.showMessage("我在主页面～")
        
        # 标题栏
        self.setWindowTitle("天气查询软件")

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


    def init_ui(self):

        # self.setFixedSize(960,700)
        
        # 创建窗口主部件
        self.main_widget = QWidget()  
        # 创建主部件的网格布局
        self.main_layout = QGridLayout()  
        # 设置窗口主部件布局为网格布局
        self.main_widget.setLayout(self.main_layout)  

        # 创建左侧部件
        self.left_widget = QWidget()  
        self.left_widget.setObjectName('left_widget')
        # 创建左侧部件的网格布局层
        self.left_layout = QGridLayout()  
        # 设置左侧部件布局为网格
        self.left_widget.setLayout(self.left_layout) 

        # 创建右侧部件
        self.right_widget = QWidget() 
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QGridLayout()
        self.right_widget.setLayout(self.right_layout) 

        # 左侧部件在第0行第0列，占8行3列
        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 5) 
        # 右侧部件在第0行第3列，占8行9列
        self.main_layout.addWidget(self.right_widget, 0, 5, 12, 7)
        # 设置窗口主部件
        self.setCentralWidget(self.main_widget) 

        # function button 
        self.single_query = QPushButton("查询今日")
        self.single_query.clicked.connect(self.request_weather)
        self.single_query.setEnabled(False)
        # self.single_query.setFixedSize(400, 30)
        self.btn_tempa = QPushButton("温度预测(可绘图)")
        self.btn_tempa.clicked.connect(self.request_weather)
        self.btn_tempa.setEnabled(False)
        self.btn_wind = QPushButton("风力预测(可绘图)")
        self.btn_wind.clicked.connect(self.request_weather)
        self.btn_wind.setEnabled(False)
        self.btn_stawea = QPushButton("综合天气预测")
        self.btn_stawea.clicked.connect(self.request_weather)
        self.btn_stawea.setEnabled(False)  
        self.left_layout.addWidget(self.single_query, 2, 0, 1, 5)
        self.left_layout.addWidget(self.btn_tempa, 3, 0, 1, 5)
        self.left_layout.addWidget(self.btn_wind, 4, 0, 1, 5)
        self.left_layout.addWidget(self.btn_stawea, 5, 0, 1, 5)

        # lineEdit to input a city
        self.city_line = QLineEdit()
        self.city_line.setPlaceholderText("输入城市回车确认")
        self.city_line.returnPressed.connect(self.match_city)
        self.left_layout.addWidget(self.city_line, 1, 0, 1, 5)

        # save figure and quit window
        self.save_fig = QPushButton("保存绘图")
        self.save_fig.setEnabled(False)
        self.save_fig.clicked.connect(self.fig_save)
        self.left_layout.addWidget(self.save_fig, 6, 0, 1, 5)

        self.load = QPushButton("写日记")
        self.left_layout.addWidget(self.load, 7, 0, 1, 5)

        self.quit_btn = QPushButton("退出")
        self.quit_btn.clicked.connect(self.quit_act)
        self.left_layout.addWidget(self.quit_btn, 8, 0, 1, 5)


        # tablewidgt to view data
        self.query_result = QTableWidget()
        self.left_layout.addWidget(self.query_result, 9, 0, 2, 5)
        self.query_result.verticalHeader().setVisible(False)


        self.label = QLabel("预测天气情况绘图展示区")
        self.right_layout.addWidget(self.label, 0, 6, 1, 7)

        self.plot_weather_wind = GraphicsLayoutWidget()
        self.plot_weather_temp = GraphicsLayoutWidget()
        self.right_layout.addWidget(self.plot_weather_temp, 1, 6, 4, 7)
        self.right_layout.addWidget(self.plot_weather_wind, 6, 6, 4, 7)

        self.setWindowOpacity(0.9) # 设置窗口透明度
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint) # 隐藏边框
        self.main_layout.setSpacing(0)

    # 按照城市的code, 请求一个城市的天气 返回 json 形式
    def request_weather(self):
        root_url = "http://t.weather.sojson.com/api/weather/city/"
        url = root_url + str(self.code)
        self.rep = get_weather.run(url)
        sender = self.sender()
        if sender.text() == "查询今日":
            self.query(1, 5, '温度', '风向', '风力', 'PM2.5', '天气描述')
        if sender.text() == "温度预测(可绘图)":
            self.btn_tempa.setEnabled(False)
            self.query(self.num, 2, '日期', '温度')
        if sender.text() == "风力预测(可绘图)":
            self.btn_wind.setEnabled(False)
            self.query(self.num, 2, '日期', '风力')
        if sender.text() == "综合天气预测":
            self.query(self.num, 4, '温度', '风向', '风力', '天气描述')

    # 读取 json 文件, 获得城市的code
    def match_city(self):
        #　输入城市后才能点击绘图
        self.btn_tempa.setEnabled(True)
        self.btn_wind.setEnabled(True)
        self.single_query.setEnabled(True)
        self.btn_stawea.setEnabled(True)
        # 在外部json文件中 读取所有城市的 code
        city = read_citycode.read_code("最新_city.json") 
        line_city = self.city_line.text() 
        # code与输入的城市对比, 如果有, 返回code, 如果没有则默认为北京
        if line_city in city.keys():
            self.code = city[line_city]
        else:
            self.code = "101010100"
            self.city_line.setText("北京")
            Qreply = QMessageBox.about(self, "你犯了一个粗误", "输入城市无效,请示新输入,否则默认为北京")

    # 保存图片成功时的提醒
    def pic_messagebox(self):
        string = '第' + str(self.filename) + '张图片.png'
        Qreply = QMessageBox.information(self, string, "已经成功保存图片到当前目录, 关闭软件后请及时拷贝走")

    # 保存图片的设置 pyqtgraph 保存无法设置图片路径
    def fig_save(self):
        ex = pe.ImageExporter(self.plt.scene())
        filename = '第' + str(self.filename) + '张图片.png'
        self.filename += 1
        ex.export(fileName = filename)
        self.pic_messagebox()

    def get_date(self, dateFormat="%Y-%m-%d", addDays=0):
        ls = []
        timeNow = datetime.datetime.now()
        key = 0
        if (addDays != 0) and key < addDays - 1:
            for i in range (addDays):
                anotherTime = timeNow + datetime.timedelta(days = key)
                anotherTime.strftime(dateFormat)
                ls.append(str(anotherTime)[0:10])
                key += 1
        else:
            anotherTime = timeNow

        return  ls

    # 查询, 可以接受多个参数, 更加灵活的查询
    def query(self, row_num, col_num, *args):
        # true value 
        tempature = self.rep.json()['data']['wendu']
        wind_power = self.rep.json()['data']['forecast'][0]['fl']
        wind_direction = self.rep.json()['data']['forecast'][0]['fx']
        pm = self.rep.json()['data']['pm25']
        type_ = self.rep.json()['data']['forecast'][0]['type']
        # forecast value
        pre_tempature = []
        pre_wind_power = []
        pre_wind_direction = []
        pre_pm = []
        pre_type_ = []

        for i in range(self.num):
            pre_tempature.append(str(self.rep.json()['data']['forecast'][i]['low']))
            pre_wind_power.append(str(self.rep.json()['data']['forecast'][i]['fl']))
            pre_wind_direction.append(str(self.rep.json()['data']['forecast'][i]['fx']))
            pre_type_.append(str(self.rep.json()['data']['forecast'][i]['type']))


        # 设置当前查询结果的行列
        self.query_result.setRowCount(row_num)  
        # 否则不会显示
        self.query_result.setColumnCount(col_num) 
        # 表头自适应伸缩
        self.query_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 按照 传入的参数设置表头, 因为每次查询的表头都不一样
        ls = [i for i in args]
        self.query_result.setHorizontalHeaderLabels(ls)

        if col_num > 2 and row_num == 1:
            item = QTableWidgetItem(str(tempature) + "℃")
            # 设置单元格文本颜色
            item.setForeground(QBrush(QColor(144, 182, 240)))
            self.query_result.setItem(0, 0, item)

            item = QTableWidgetItem(str(wind_direction))
            item.setForeground(QBrush(QColor(144, 182, 240)))
            self.query_result.setItem(0, 1, item)

            item = QTableWidgetItem(str(wind_power))
            item.setForeground(QBrush(QColor(144, 182, 240)))
            self.query_result.setItem(0, 2, item)

            item = QTableWidgetItem(str(pm))
            item.setForeground(QBrush(QColor(144, 182, 240)))
            self.query_result.setItem(0, 3, item)
            
            item = QTableWidgetItem(str(type_))
            item.setForeground(QBrush(QColor(144, 182, 240)))                    
            self.query_result.setItem(0, 4, item)
                
        if col_num > 2 and row_num > 1:
            for i in range (0, self.num):
                item = QTableWidgetItem("最" + str(pre_tempature[i]))
                # 设置单元格文本颜色
                item.setForeground(QBrush(QColor(144, 182, 240)))
                self.query_result.setItem(i, 0, item)

                item = QTableWidgetItem(str(pre_wind_direction[i]))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                self.query_result.setItem(i, 1, item)

                item = QTableWidgetItem(str(pre_wind_power[i]))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                self.query_result.setItem(i, 2, item)
                
                item = QTableWidgetItem(str(pre_type_[i]))
                item.setForeground(QBrush(QColor(144, 182, 240)))                    
                self.query_result.setItem(i, 3, item)

        if col_num == 2 and row_num > 1:
            date = self.get_date(addDays=self.num)
            key = 0
            for i in date:
                item = QTableWidgetItem(i)
                item.setForeground(QBrush(QColor(144, 182, 240)))  
                self.query_result.setItem(key, 0, item)
                key += 1              
            if self.query_result.horizontalHeaderItem(1).text() == '温度':
                key = 0
                for i in pre_tempature:
                    item = QTableWidgetItem("最" + i)
                    item.setForeground(QBrush(QColor(144, 182, 240)))  
                    self.query_result.setItem(key, 1, item)
                    key += 1
            if self.query_result.horizontalHeaderItem(1).text() == '风力':
                key = 0
                for i in pre_wind_power:
                    item = QTableWidgetItem(i)
                    item.setForeground(QBrush(QColor(144, 182, 240)))  
                    self.query_result.setItem(key, 1, item)
                    key += 1               

        # 只有两列的时候才可以绘制图像, 
        if col_num < 4:
            ls, y = [], []
            x = np.linspace(1, self.num, self.num)
            # 将 treeview 里面的结果以数字的形式返回到列表中, 用于绘图
            for row in range(self.num):
                str1 = str(self.query_result.item(row, 1).text())
                ls.extend(re.findall(r'\d+(?:\.\d+)?', str1))
            if len(ls) == 5:
                y = [float(i) for i in ls]
            if len(ls) == 10:
                lt = [float(i) for i in ls]
                for i in range (0, len(lt), 2):
                    y.append((lt[i] + lt[i + 1]) / 2)
            if len(ls) == 5:
                y = [float(i) for i in ls]
            else:
                y = [float(i) for i in ls[0:5]]
            # 获取 treeview 的标题, 以得到绘图时的标得
            if self.query_result.horizontalHeaderItem(1).text() == '温度':
                title_ = "近期一个月温度变化（预测）"
            if self.query_result.horizontalHeaderItem(1).text() == '风力':
                title_ = "近期一个月风力变化（预测）"
            # 绘图时先清空面板 否则会新加一列,效果不好 
            # 且 pyqtgraph 的新加一列有bug, 效果不是很好 下次使用 matplotlib
            if title_ == "近期一个月风力变化（预测）":
                self.plot_weather_wind.clear()
                bg1 = pg.BarGraphItem(x=x, height=y, width=0.3, brush=QColor(137, 232, 165))
                self.plt1 = self.plot_weather_wind.addPlot(title = title_)
                self.plt1.addItem(bg1)
            if title_ == "近期一个月温度变化（预测）":
                self.plot_weather_temp.clear()
                self.plt = self.plot_weather_temp.addPlot(title = title_)
                bg2 = pg.BarGraphItem(x=x, height=y, width=0.3, brush=QColor(32, 235, 233))
                self.plt.addItem(bg2)
            # 绘图后才可以保存图片
            self.save_fig.setEnabled(True)

    # 退出按钮
    def quit_act(self):
        # sender 是发送信号的对象
        sender = self.sender()
        print(sender.text() + '键被按下')
        qApp = QApplication.instance()
        qApp.quit()

    def center(self):
        '''
        获取桌面长宽
        获取窗口长宽
        移动
        '''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

def main():
    app = QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()