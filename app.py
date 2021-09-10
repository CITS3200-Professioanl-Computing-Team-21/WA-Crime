import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets, QtCore
from ui import Ui_MainWindow

# BUTTON IDENTIFIERS
STATION = 0
DISTRICT = 1
REGION = 2
YEAR = 3
MONTH = 4
QUARTER = 5
CRIME = 6

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
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

        # inital configuration
        self.cache_zone_type = "Region"
        self.cache_zone = "All"
        self.cache_year = "All"
        self.cache_period = "All"
        self.cache_crime = "All"

        # callback function when dropdown option changed
        self.Station_comboxBox.currentIndexChanged.connect(lambda : self.generate_map(STATION))
        self.District_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(DISTRICT))
        self.Region_comboBox_3.currentIndexChanged.connect(lambda : self.generate_map(REGION))
        self.Quarterly_comboBox_4.currentIndexChanged.connect(lambda : self.generate_map(QUARTER))
        self.Monthly_comboBox_5.currentIndexChanged.connect(lambda : self.generate_map(MONTH))
        self.Year_comboBox_6.currentIndexChanged.connect(lambda : self.generate_map(YEAR))
        self.Type_comboBox_7.currentIndexChanged.connect(lambda : self.generate_map(CRIME))

    # Reads csv file from config, outputs a list of names 
    # filename is the name of file
    def readfile(self,filename):
        fd = open("./config/"+filename, "r")
        data = fd.read()
        fd.close()
        return data.split(",")

    
    # redisplays new map based on selectors
    def generate_map(self, src):
        # update current dropdown options
        if src == STATION:
            self.cache_zone_type = "Station"
            self.cache_zone = self.Station_comboxBox.currentText()
        elif src == DISTRICT:
            self.cache_zone_type = "District"
            self.cache_zone = self.District_comboBox_2.currentText()
        elif src == REGION:
            self.cache_zone_type = "Region"
            self.cache_zone = self.Region_comboBox_3.currentText()
        elif src == QUARTER:
            self.cache_period = self.Quarterly_comboBox_4.currentText()
        elif src == MONTH:
            self.cache_period = self.Monthly_comboBox_5.currentText()
        elif src == YEAR:
            self.cache_year = self.Year_comboBox_6.currentText()
        elif src == CRIME:
            self.cache_crime = self.Type_comboBox_7.currentText()

        # generates new html (placeholder for front end)
        self.stub(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime)

        # updates html display with new html
        url = QtCore.QUrl.fromLocalFile("/testlayers.html")
        self.browser.load(url)

    # placeholder, function generates a html based on input query
    def stub(self,name, zone_type, year, period, crime):
        print("Name, Zone_type, Year, Period, Crime")
        print(name, zone_type, year, period, crime)

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