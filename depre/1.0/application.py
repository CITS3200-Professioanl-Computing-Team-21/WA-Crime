# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'application.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

# from PyQt html display.py
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

# UI application display
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1114, 684)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Folium map
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 1081, 621))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.Map = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.Map.setContentsMargins(0, 0, 0, 0)
        self.Map.setObjectName("Map")
        #from PyQt html display.py
        self.webView = QWebEngineView()
        url = QtCore.QUrl.fromLocalFile("/testpins.html")
        self.webView.load(url)
        self.Map.addWidget(self.webView)

        # Crime, Location, Time Selectors
        self.Selectors_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.Selectors_2.setGeometry(QtCore.QRect(20, 400, 171, 221))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Selectors_2.setFont(font)
        self.Selectors_2.setObjectName("Selectors_2")
        self.Selectors = QtWidgets.QVBoxLayout(self.Selectors_2)
        self.Selectors.setObjectName("Selectors")
        self.Crime_label = QtWidgets.QLabel(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Crime_label.sizePolicy().hasHeightForWidth())
        self.Crime_label.setSizePolicy(sizePolicy)
        self.Crime_label.setObjectName("Crime_label")
        self.Selectors.addWidget(self.Crime_label)
        self.Crime_dropdown = QtWidgets.QComboBox(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Crime_dropdown.sizePolicy().hasHeightForWidth())
        self.Crime_dropdown.setSizePolicy(sizePolicy)
        self.Crime_dropdown.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Crime_dropdown.setObjectName("Crime_dropdown")
        self.Crime_dropdown.addItem("")
        self.Crime_dropdown.addItem("")
        self.Selectors.addWidget(self.Crime_dropdown)
        self.Location_label = QtWidgets.QLabel(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Location_label.sizePolicy().hasHeightForWidth())
        self.Location_label.setSizePolicy(sizePolicy)
        self.Location_label.setObjectName("Location_label")
        self.Selectors.addWidget(self.Location_label)
        self.Location_dropdown = QtWidgets.QComboBox(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Location_dropdown.sizePolicy().hasHeightForWidth())
        self.Location_dropdown.setSizePolicy(sizePolicy)
        self.Location_dropdown.setObjectName("Location_dropdown")
        self.Location_dropdown.addItem("")
        self.Location_dropdown.addItem("")
        self.Selectors.addWidget(self.Location_dropdown)
        self.Time_label = QtWidgets.QLabel(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Time_label.sizePolicy().hasHeightForWidth())
        self.Time_label.setSizePolicy(sizePolicy)
        self.Time_label.setObjectName("Time_label")
        self.Selectors.addWidget(self.Time_label)
        self.Time_dropdown = QtWidgets.QComboBox(self.Selectors_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Time_dropdown.sizePolicy().hasHeightForWidth())
        self.Time_dropdown.setSizePolicy(sizePolicy)
        self.Time_dropdown.setObjectName("Time_dropdown")
        self.Time_dropdown.addItem("")
        self.Time_dropdown.addItem("")
        self.Selectors.addWidget(self.Time_dropdown)

        # placeholder for infomation display
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(920, 20, 161, 601))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.Info_display = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.Info_display.setContentsMargins(0, 0, 0, 0)
        self.Info_display.setObjectName("Info_display")

        # default menu and status bars
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1114, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        # callback function when dropdown option changed
        self.Crime_dropdown.currentIndexChanged.connect(self.generate_map)
        self.Time_dropdown.currentIndexChanged.connect(self.generate_map)
        self.Location_dropdown.currentIndexChanged.connect(self.generate_map)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Crime_label.setText(_translate("MainWindow", "Crime"))
        self.Crime_dropdown.setItemText(0, _translate("MainWindow", "crime1"))
        self.Crime_dropdown.setItemText(1, _translate("MainWindow", "crime2"))
        self.Location_label.setText(_translate("MainWindow", "Location"))
        self.Location_dropdown.setItemText(0, _translate("MainWindow", "loc1"))
        self.Location_dropdown.setItemText(1, _translate("MainWindow", "loc2"))
        self.Time_label.setText(_translate("MainWindow", "Time"))
        self.Time_dropdown.setItemText(0, _translate("MainWindow", "time1"))
        self.Time_dropdown.setItemText(1, _translate("MainWindow", "time2"))

    # redisplays new map based on selectors
    def generate_map(self):
        # get current dropdown options
        '''
        self.Crime_dropdown.currentText
        self.Time_dropdown.currentText
        self.Location_dropdown.currentText
        '''

        # generates new html (placeholder for front end)

        # sets new html
        url = QtCore.QUrl.fromLocalFile("/testlayers.html")
        self.webView.load(url)

# Reads csv file from config, outputs a list of names 
# filename is the name of file
def readfile(filename):
    fd = open("./config/"+filename, "r")
    data = fd.read()
    fd.close()
    return data.split(",")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
