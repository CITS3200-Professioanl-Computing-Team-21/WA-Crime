import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets, QtCore
from ui import Ui_MainWindow
import boundaries

# IDENTIFIERS
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
        # initialise widgets from ui.py
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.browser = QWebEngineView()
        self.browser.load(QtCore.QUrl.fromLocalFile("/default.html"))
        hboxlayout = QHBoxLayout(self.frame)
        hboxlayout.addWidget(self.browser)

        # export button
        self.Search_pushButton.clicked.connect(self.query)
        self.Screenshot_pushButton.clicked.connect(self.screenshot)

        # search box prompt
        self.lineEdit.setPlaceholderText("Name,Zone_type,Year,Period,Crime")

        # initialises combo boxes options from csv in ./config
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

        # inital configuration [all,region,all,all,all]
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

    # generates a new html and displays it
    def updatehtml(self):
        # generates new html (placeholder for front end)
        self.process_query(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime)

        # updates html display with new html
        #url = QtCore.QUrl.fromLocalFile("/generated_map.html")
        url = QtCore.QUrl.fromLocalFile("/trial.html")
        self.browser.load(url)
    
    # placeholder, function generates a html based on input query
    def process_query(self,name, zone_type, year, period, crime):
        print("Name, Zone_type, Year, Period, Crime")
        print(name, zone_type, year, period, crime)
        output = boundaries.choropleth([name, zone_type, year, period, crime])

    # callback function that redisplays new map based on selectors
    # src is the source(dropdown) that cause the update
    # will only activate if unlocked (self.update == true)
    def generate_map(self, src):
        if self.update:
            # update current dropdown options
            # zone selectors
            if src == STATION:
                self.cache_zone_type = "station"
                self.cache_zone = self.Station_comboBox.currentText() # cache current selection for html generation
                self.update = False                         # setCurrentIndex calls the callback, lock prevent looping
                self.District_comboBox.setCurrentIndex(-1)  # deselect other selectors 
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

            # period selectors 
            # prevents invalid input queries based on selector.doc
            elif src == QUARTER:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(-1)
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Quarterly_comboBox_1.currentIndex() <= 0:   # if all in quarter1, deselect option in quarter2
                    self.update = False
                    self.Quarterly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                # updating cache of changes
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                if self.Quarterly_comboBox_2.currentIndex() >= 1:   # if option selected in quarter2
                    self.cache_period += "-"+self.Quarterly_comboBox_2.currentText()
            elif src == QUARTER2:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(-1)
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.update = True
                if self.Quarterly_comboBox_1.currentIndex() == self.Quarterly_comboBox_2.currentIndex() or \
                self.Quarterly_comboBox_1.currentIndex() <= 0:      # disallow similar options in both
                    self.update = False
                    self.Quarterly_comboBox_2.setCurrentIndex(-1)
                    self.update = True
                    return False
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                if self.Quarterly_comboBox_2.currentIndex() >= 1:
                    self.cache_period += "-"+self.Quarterly_comboBox_2.currentText()
            elif src == MONTH:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(-1)  
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
            
            # year selector
            elif src == YEAR:
                if self.Year_comboBox_1.currentIndex() <= self.Year_comboBox_2.currentIndex() or \
                self.Year_comboBox_1.currentIndex() == 0: # disallow years out of order
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
            
            #crime selector
            elif src == CRIME:
                self.cache_crime = self.Crime_comboBox.currentText()

            # updates the query to the search box
            self.lineEdit.setText("{},{},{},{},{}".format(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime))

            self.updatehtml()
            return True

    # Search Button
    # check if input query is valid via finding corresponding dropdowns options (and selecting them)
    def query(self):
        text = self.lineEdit.text().split(",") # line edit is the search box
        # check num args
        if (len(text) != 5):
            QMessageBox.warning(self,"Error","Invalid query format")
            return False
        
        # checking zone
        if (text[1] not in ["station","district","region","suburb"]):
            QMessageBox.warning(self,"Error","Invalid zone_type")
            return False
        else:
            if text[1] == "station":
                if (self.Station_comboBox.findText(text[0]) == -1):
                    QMessageBox.warning(self,"Error","Invalid station")
                    return False
                else:
                    # updates corresponding dropdown and caches new value
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
                    QMessageBox.warning(self,"Error","Invalid district")
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
                    QMessageBox.warning(self,"Error","Invalid region")
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
                    QMessageBox.warning(self,"Error","Invalid suburb")
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

        # checking year
        if text[2] == "all":
            self.update = False
            self.Year_comboBox_1.setCurrentIndex(0)
            self.Year_comboBox_2.setCurrentIndex(-1)
            self.cache_year = self.Year_comboBox_1.currentText()
            self.update = True
        else:
            buf = text[2].split("-")
            if len(buf) == 2 and self.Year_comboBox_1.findText(text[2]) != -1:   #single year (2012-13)
                self.update = False
                self.Year_comboBox_1.setCurrentIndex(self.Year_comboBox_1.findText(text[2]))
                self.Year_comboBox_2.setCurrentIndex(-1)
                self.cache_year = self.Year_comboBox_1.currentText()
                self.update = True
            elif len(buf) == 4:   #year range (2012-13 - 2014-15)
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
                    QMessageBox.warning(self,"Error","Invalid year range")
                    return False
            else:
                QMessageBox.warning(self,"Error","Invalid year")
                return False

        #check month/quarter
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
                QMessageBox.warning(self,"Error","Invalid month")
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
                QMessageBox.warning(self,"Error","Invalid quarter")
                return False
        else:
            QMessageBox.warning(self,"Error","Invalid period")
            return False

        # check crime
        if (self.Crime_comboBox.findText(text[4]) == -1):
            QMessageBox.warning(self,"Error","Invalid crime_type")
            return False
        else:
            self.update = False
            self.Crime_comboBox.setCurrentIndex(self.Crime_comboBox.findText(text[4]))
            self.cache_crime = self.Crime_comboBox.currentText()
            self.update = True

        self.updatehtml()
        return True

    # Function for Screenshot button    
    def screenshot(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                "Save Image",
                                                                "./",  # initial dir
                                                                ".jpg")

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.frame.winId())
        screenshot.save(fileName_choose, 'jpg')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())