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
SUBURB = 7
YEAR2 = 8
MONTH2 = 9
QUARTER2 = 10
MONTHS = ['all','jul','aug','sep','oct','nov','dec','jan','feb','mar','apr','may','jun']
QUARTERS = ['all','q3','q4','q1','q2']

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.showHtml()
        self.Search_pushButton.clicked.connect(self.query)
        self.Screenshot_pushButton.clicked.connect(self.screenshot)

        # initalises combo boxes options from csv in ./config
        self.Station_comboBox.addItems(self.readfile("stations.csv"))
        self.District_comboBox.addItems(self.readfile("districts.csv"))
        self.Region_comboBox.addItems(self.readfile("regions.csv"))
        self.Suburb_comboBox.addItems(self.readfile("suburbs.csv"))
        self.Year_comboBox_1.addItems(self.readfile("years.csv"))
        self.Year_comboBox_2.addItems(self.readfile("years.csv"))
        self.Monthly_comboBox_1.addItems(MONTHS)
        self.Monthly_comboBox_2.addItems(MONTHS)
        self.Quarterly_comboBox_1.addItems(QUARTERS)
        self.Quarterly_comboBox_2.addItems(QUARTERS)
        self.Crime_comboBox.addItems(self.readfile("crime_types.csv"))
        self.Year_comboBox_2.setItemText(0,"")  # remove all for second dropdown
        self.Monthly_comboBox_2.setItemText(0,"") 
        self.Quarterly_comboBox_2.setItemText(0,"")

        # inital configuration
        self.cache_zone_type = "region"
        self.cache_zone = "all"
        self.cache_year = "all"
        self.cache_period = "all"
        self.cache_crime = "all"
        self.Station_comboBox.setCurrentIndex(-1)
        self.District_comboBox.setCurrentIndex(-1)
        self.Suburb_comboBox.setCurrentIndex(-1)
        self.Year_comboBox_2.setCurrentIndex(-1)
        self.Quarterly_comboBox_1.setCurrentIndex(-1)
        self.Quarterly_comboBox_2.setCurrentIndex(-1)
        self.Monthly_comboBox_1.setCurrentIndex(-1)
        self.Monthly_comboBox_2.setCurrentIndex(-1)
        self.lineEdit.setPlaceholderText("Name,Zone_type,Year,Period,Crime")

        # make Zone and Crime combo boxes searchable
        self.Station_comboBox.setEditable(True)
        self.Station_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Station_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.District_comboBox.setEditable(True)
        self.District_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.District_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.Region_comboBox.setEditable(True)
        self.Region_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Region_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.Suburb_comboBox.setEditable(True)
        self.Suburb_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Suburb_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.Crime_comboBox.setEditable(True)
        self.Crime_comboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Crime_comboBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # callback function when dropdown option changed
        self.update = True #allows dropdown updates, prevents looping updates
        self.Crime_comboBox.currentIndexChanged.connect(lambda : self.generate_map(CRIME))
        self.Region_comboBox.currentIndexChanged.connect(lambda : self.generate_map(REGION))
        self.District_comboBox.currentIndexChanged.connect(lambda : self.generate_map(DISTRICT))
        self.Station_comboBox.currentIndexChanged.connect(lambda : self.generate_map(STATION))
        self.Suburb_comboBox.currentIndexChanged.connect(lambda : self.generate_map(SUBURB))
        self.Year_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(YEAR))
        self.Year_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(YEAR2))
        self.Monthly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(MONTH))
        self.Monthly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(MONTH2))
        self.Quarterly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(QUARTER))
        self.Quarterly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(QUARTER2))

    # Reads csv file from config, outputs a list of names 
    # filename is the name of file
    def readfile(self,filename):
        fd = open("./config/"+filename, "r")
        data = fd.read()
        fd.close()
        return data.split(",")

    
    # redisplays new map based on selectors
    def generate_map(self, src):
        if self.update:
            # update current dropdown options
            if src == STATION:
                self.cache_zone_type = "station"
                self.cache_zone = self.Station_comboBox.currentText() # store current selection
                self.update = False
                self.District_comboBox.setCurrentIndex(-1) # deselect other selectors 
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == DISTRICT:
                self.cache_zone_type = "district"
                self.cache_zone = self.District_comboBox.currentText()
                self.update = False
                self.Station_comboBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == REGION:
                self.cache_zone_type = "region"
                self.cache_zone = self.Region_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == SUBURB:
                self.cache_zone_type = "suburb"
                self.cache_zone = self.Suburb_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == QUARTER:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(-1)
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Quarterly_comboBox_1.currentIndex() <= 0:
                    self.update = False
                    self.Quarterly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                if self.Quarterly_comboBox_2.currentIndex() >= 1:
                    self.cache_period += "-"+self.Quarterly_comboBox_2.currentText()
            elif src == QUARTER2:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(-1)
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Quarterly_comboBox_1.currentIndex() == self.Quarterly_comboBox_2.currentIndex() or \
                self.Quarterly_comboBox_1.currentIndex() <= 0:
                    self.update = False
                    self.Quarterly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                    return False
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                if self.Quarterly_comboBox_2.currentIndex() >= 1:
                    self.cache_period += "-"+self.Quarterly_comboBox_2.currentText()
            elif src == MONTH:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(-1)   # deselect quarters
                self.Quarterly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Monthly_comboBox_1.currentIndex() <= 0:
                    self.update = False
                    self.Monthly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                self.cache_period = self.Monthly_comboBox_1.currentText()
                if self.Monthly_comboBox_2.currentIndex() >= 1:
                    self.cache_period += "-"+self.Monthly_comboBox_2.currentText()
            elif src == MONTH2:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(-1)
                self.Quarterly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Monthly_comboBox_1.currentIndex() == self.Monthly_comboBox_2.currentIndex() or \
                self.Monthly_comboBox_1.currentIndex() <= 0:
                    self.update = False
                    self.Monthly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                    return False
                self.cache_period = self.Monthly_comboBox_1.currentText()
                if self.Monthly_comboBox_2.currentIndex() >= 1:
                    self.cache_period += "-"+self.Monthly_comboBox_2.currentText()
            elif src == YEAR:
                if self.Year_comboBox_1.currentIndex() <= self.Year_comboBox_2.currentIndex() or self.Year_comboBox_1.currentIndex() == 0:
                    self.update = False
                    self.Year_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                self.cache_year = self.Year_comboBox_1.currentText()                    
                if self.Year_comboBox_2.currentIndex() >= 1:
                    self.cache_year += "-"+self.Year_comboBox_2.currentText()
            elif src == YEAR2:
                if self.Year_comboBox_1.currentIndex() <= self.Year_comboBox_2.currentIndex():
                    self.update = False
                    self.Year_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                    return False
                self.cache_year = self.Year_comboBox_1.currentText()                    
                if self.Year_comboBox_2.currentIndex() >= 1:
                    self.cache_year += "-"+self.Year_comboBox_2.currentText()
            elif src == CRIME:
                self.cache_crime = self.Crime_comboBox.currentText()

            # generates new html (placeholder for front end)
            self.stub(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime)
            self.lineEdit.setText("{},{},{},{},{}".format(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime))

            # updates html display with new html
            url = QtCore.QUrl.fromLocalFile("/regions.html")
            self.browser.load(url)
            return True

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

    # Search Button
    def query(self):
        text = self.lineEdit.text().split(",") # line edit is the search box
        print(text)
        # check num args
        if (len(text) != 5):
            print("invalid number of args")
            return False
        
        # checking zone
        if (text[1] not in ["station","district","region","suburb"]):
            print("invalid Zone")
            return False
        else:
            if text[1] == "station":
                if (self.Station_comboBox.findText(text[0]) == -1):
                    print("invalid Station")
                    return False
                else:
                    self.update = False
                    self.Station_comboBox.setCurrentIndex(self.Station_comboBox.findText(text[0]))
                    self.District_comboBox.setCurrentIndex(-1)
                    self.Suburb_comboBox.setCurrentIndex(-1)
                    self.Region_comboBox.setCurrentIndex(-1)
                    self.cache_zone = self.Station_comboBox.currentText()
                    self.cache_zone_type = "station"
                    self.update = True
            elif text[1] == "district":
                if (self.District_comboBox.findText(text[0]) == -1):
                    print("invalid District")
                    return False
                else:
                    self.update = False
                    self.District_comboBox.setCurrentIndex(self.District_comboBox.findText(text[0]))
                    self.Suburb_comboBox.setCurrentIndex(-1)
                    self.Station_comboBox.setCurrentIndex(-1)
                    self.Region_comboBox.setCurrentIndex(-1)
                    self.cache_zone = self.District_comboBox.currentText()
                    self.cache_zone_type = "district"
                    self.update = True
            elif text[1] == "region":
                if (self.Region_comboBox.findText(text[0]) == -1):
                    print("invalid Region")
                    return False
                else:
                    self.update = False
                    self.Region_comboBox.setCurrentIndex(self.Suburb_comboBox.findText(text[0]))
                    self.District_comboBox.setCurrentIndex(-1)
                    self.Station_comboBox.setCurrentIndex(-1)
                    self.Suburb_comboBox.setCurrentIndex(-1)
                    self.cache_zone = self.Region_comboBox.currentText()
                    self.cache_zone_type = "region"
                    self.update = True
            elif text[1] == "suburb":
                if (self.Suburb_comboBox.findText(text[0]) == -1):
                    print("invalid Suburb")
                    return False
                else:
                    self.update = False
                    self.Suburb_comboBox.setCurrentIndex(self.Suburb_comboBox.findText(text[0]))
                    self.District_comboBox.setCurrentIndex(-1)
                    self.Station_comboBox.setCurrentIndex(-1)
                    self.Region_comboBox.setCurrentIndex(-1)
                    self.cache_zone = self.Suburb_comboBox.currentText()
                    self.cache_zone_type = "suburb"
                    self.update = True

        # check year
        if text[2] == "all":
            self.update = False
            self.Year_comboBox_1.setCurrentIndex(0)
            self.Year_comboBox_2.setCurrentIndex(-1)
            self.cache_year = self.Year_comboBox_1.currentText()
            self.update = True
        else:
            buf = text[2].split("-")
            if len(buf) == 2 and self.Year_comboBox_1.findText(text[2]) != -1:   #single year
                self.update = False
                self.Year_comboBox_1.setCurrentIndex(self.Year_comboBox_1.findText(text[2]))
                self.Year_comboBox_2.setCurrentIndex(-1)
                self.cache_year = self.Year_comboBox_1.currentText()
                self.update = True
            elif len(buf) == 4:   #year range
                buf = [buf[0]+"-"+buf[1],buf[2]+"-"+buf[3]]
                i = self.Year_comboBox_1.findText(buf[0])
                j = self.Year_comboBox_2.findText(buf[1])
                if i != -1 and j != -1 and i>j:
                    self.update = False
                    self.Year_comboBox_1.setCurrentIndex(i)
                    self.Year_comboBox_2.setCurrentIndex(j)
                    self.cache_year = self.Year_comboBox_1.currentText()+"-"+self.Year_comboBox_2.currentText()
                    self.update = True
                else:
                    print("invalid Years")
                    return False
            else:
                print("invalid Year")
                return False

        #check month/quarter
        MONTHS = ['all','jul','aug','sep','oct','nov','dec','jan','feb','mar','apr','may','jun']
        QUARTERS = ['all','q3','q4','q1','q2']
        buf = text[3].split("-")
        if buf[0] in MONTHS:
            self.Quarterly_comboBox_1.setCurrentIndex(-1)
            self.Quarterly_comboBox_2.setCurrentIndex(-1)
            if len(buf) == 1:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(self.Monthly_comboBox_1.findText(text[3]))
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.cache_period = self.Monthly_comboBox_1.currentText()
                self.update = True
            elif len(buf) == 2 and buf[1] in MONTHS:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(self.Monthly_comboBox_1.findText(buf[0]))
                self.Monthly_comboBox_2.setCurrentIndex(self.Monthly_comboBox_2.findText(buf[1]))
                self.cache_period = self.Monthly_comboBox_1.currentText()+"-"+self.Monthly_comboBox_2.currentText()
                self.update = True
            else:
                print("invalid Period")
                return False

        elif buf[0] in QUARTERS:
            self.Monthly_comboBox_1.setCurrentIndex(-1)
            self.Monthly_comboBox_2.setCurrentIndex(-1)
            if len(buf) == 1:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(self.Quarterly_comboBox_1.findText(text[3]))
                self.Quarterly_comboBox_2.setCurrentIndex(-1)
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                self.update = True
            elif len(buf) == 2 and buf[1] in QUARTERS:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(self.Quarterly_comboBox_1.findText(buf[0]))
                self.Quarterly_comboBox_2.setCurrentIndex(self.Quarterly_comboBox_2.findText(buf[1]))
                self.cache_period = self.Quarterly_comboBox_1.currentText()+"-"+self.Quarterly_comboBox_2.currentText()
                self.update = True
            else:
                print("invalid Period")
                return False
        else:
            print("invalid Period")
            return False

        # check crime
        if (self.Crime_comboBox.findText(text[4]) == -1):
            print("invalid number of Crime")
            return False
        else:
            self.update = False
            self.Crime_comboBox.setCurrentIndex(self.Crime_comboBox.findText(text[4]))
            self.cache_crime = self.Crime_comboBox.currentText()
            self.update = True

        # generates new html (placeholder for front end)
        self.stub(text[0], text[1], text[2], text[3], text[4])

        # updates html display with new html
        url = QtCore.QUrl.fromLocalFile("/stations.html")
        self.browser.load(url)
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())