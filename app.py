import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets
from ui import Ui_MainWindow

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.setting()
        self.showHtml()
        self.search_pushButton_2.clicked.connect(self.back)
        self.spinBox.valueChanged.connect(self.change_table)
        self.Screenshot_pushButton.clicked.connect(self.screenshot)

        # make Zone and Crime combo boxes searchable
        self.Station_comboxBox.setEditable(True)
        self.Station_comboxBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Station_comboxBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.District_comboBox_2.setEditable(True)
        self.District_comboBox_2.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.District_comboBox_2.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.Region_comboBox_3.setEditable(True)
        self.Region_comboBox_3.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Region_comboBox_3.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.Type_comboBox_7.setEditable(True)
        self.Type_comboBox_7.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Type_comboBox_7.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # initalises combo boxes options from csv in ./config
        self.Station_comboxBox.addItems(self.readfile("stations.csv"))
        self.District_comboBox_2.addItems(self.readfile("districts.csv"))
        self.Region_comboBox_3.addItems(self.readfile("regions.csv"))
        self.Year_comboBox_6.addItems(self.readfile("years.csv"))
        MONTHS = ['Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun']
        self.Monthly_comboBox_5.addItems(MONTHS)
        QUARTERS = ['Jul-Sep','Oct-Dec','Jan-Mar','Apr-Jun'] 
        self.Quarterly_comboBox_4.addItems(QUARTERS)
        self.Type_comboBox_7.addItems(self.readfile("crime_types.csv"))

    # Reads csv file from config, outputs a list of names 
    # filename is the name of file
    def readfile(self,filename):
        fd = open("./config/"+filename, "r")
        data = fd.read()
        fd.close()
        return data.split(",")

    # Function for Screenshot button    
    def screenshot(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                "Save Image",
                                                                "./",  # initial dir
                                                                ".jpg")

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.frame.winId())
        screenshot.save(fileName_choose, 'jpg')
        #QMessageBox.warning(self,"Tips","Finished!",QMessageBox.Yes,QMessageBox.Yes)

    # Function to load html
    def showHtml(self):
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.google.com"))
        hboxlayout = QHBoxLayout(self.frame)
        hboxlayout.addWidget(self.browser)

    # Changes the font of UI
    def change_table(self):
        self.setStyleSheet(f"font:{self.spinBox.value()}px")

    # Search Button
    def back(self):
        text = self.lineEdit.text()
        print(text.split())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())