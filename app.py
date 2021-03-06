import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets, QtCore
from ui import Ui_MainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal
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

# threaded worker used to generate html
class Worker(QObject):
    finished = pyqtSignal()
    obj = "" # window object reference

    # runs backend map generation
    def run(self):
        print("Name, Zone_type, Year, Period, Crime")
        print(self.obj.cache_zone, self.obj.cache_zone_type, self.obj.cache_year, self.obj.cache_period, self.obj.cache_crime)
        self.obj.cache_data = boundaries.choropleth([self.obj.cache_zone, self.obj.cache_zone_type, self.obj.cache_year, self.obj.cache_period, self.obj.cache_crime])
        self.finished.emit()

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        # initialise widgets from ui.py
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.browser = QWebEngineView()
        self.browser.load(QtCore.QUrl.fromLocalFile("/generated_map.html"))
        hboxlayout = QHBoxLayout(self.frame)
        hboxlayout.addWidget(self.browser)
        
        # self.Search_pushButton.clicked.connect(self.query)                 # moved to ui.py
        self.Screenshot_pushButton.clicked.connect(self.screenshot)          # export button
        self.cache_data = boundaries.choropleth(["all","region","all","all","all"])
        self.Summary_pushButton.clicked.connect(lambda : self.cache_data.getGraph())

        self.lineEdit.setPlaceholderText("Name,Zone_type,Year,Period,Crime") # search box prompt
        self.textEdit.setReadOnly(True)                                      # anomolies display

        # initialises combo boxes options from csv in ./config
        self.Station_comboxBox.addItems(self.readfile("stations.csv"))
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
        self.Station_comboxBox.setCurrentIndex(-1)
        self.District_comboBox.setCurrentIndex(-1)
        self.Suburb_comboBox.setCurrentIndex(-1)
        self.Year_comboBox_2.setCurrentIndex(-1)
        self.Quarterly_comboBox_1.setCurrentIndex(-1)
        self.Quarterly_comboBox_2.setCurrentIndex(-1)
        self.Monthly_comboBox_1.setCurrentIndex(-1)
        self.Monthly_comboBox_2.setCurrentIndex(-1)

        # make Zone and Crime combo boxes searchable
        self.Station_comboxBox.setEditable(True)
        self.Station_comboxBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.Station_comboxBox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
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
        self.Station_comboxBox.currentIndexChanged.connect(lambda : self.generate_map(STATION))
        self.Suburb_comboBox.currentIndexChanged.connect(lambda : self.generate_map(SUBURB))
        self.Year_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(YEAR))
        self.Year_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(YEAR2))
        self.Monthly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(MONTH))
        self.Monthly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(MONTH2))
        self.Quarterly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(QUARTER))
        self.Quarterly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(QUARTER2))

        # initialise layout events
        self.initDrag()

    # Reads csv file from config, outputs a list of names 
    # filename is the name of file
    def readfile(self,filename):
        fd = open("./config/"+filename, "r")
        data = fd.read()
        fd.close()
        return data.split(",")

    # generates a new html and displays it
    # thread allows client responsivenes while html is being generated
    def updatehtml(self):
        if self.update: # ignore if already generating
            self.update = False
            self.allow_input(False) # block new inputs

            # create thread
            self.thread = QThread()
            self.worker = Worker()
            self.worker.obj = self
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.post_update)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    # updates client post html generation
    def post_update(self):
        url = QtCore.QUrl.fromLocalFile("/generated_map.html")
        self.browser.load(url)
        self.allow_input(True)
        self.textEdit.setText(self.cache_data.getText())
        self.update = True  # release lock
    
    # prevents new inputs will html is generating
    def allow_input(self,s):
        self.lineEdit.setEnabled(s)
        self.Crime_comboBox.setEnabled(s)
        self.Region_comboBox.setEnabled(s)
        self.District_comboBox.setEnabled(s)
        self.Station_comboxBox.setEnabled(s)
        self.Suburb_comboBox.setEnabled(s)
        self.Year_comboBox_1.setEnabled(s)
        self.Year_comboBox_2.setEnabled(s)
        self.Monthly_comboBox_1.setEnabled(s)
        self.Monthly_comboBox_2.setEnabled(s)
        self.Quarterly_comboBox_1.setEnabled(s)
        self.Quarterly_comboBox_2.setEnabled(s)
        
    # callback function that redisplays new map based on selectors
    # src is the source(dropdown) that cause the update
    # will only activate if unlocked (self.update == true)
    def generate_map(self, src):
        if self.update:
            # update current dropdown options
            # zone selectors
            if src == STATION:
                self.cache_zone_type = "station"
                self.cache_zone = self.Station_comboxBox.currentText() # cache current selection for html generation
                self.update = False                         # setCurrentIndex calls the callback, lock prevent looping
                self.District_comboBox.setCurrentIndex(-1)  # deselect other selectors 
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == DISTRICT:
                self.cache_zone_type = "district"
                self.cache_zone = self.District_comboBox.currentText()
                self.update = False
                self.Station_comboxBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == REGION:
                self.cache_zone_type = "region"
                self.cache_zone = self.Region_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboxBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == SUBURB:
                self.cache_zone_type = "suburb"
                self.cache_zone = self.Suburb_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboxBox.setCurrentIndex(-1)
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
        if self.update:
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
                    if (self.Station_comboxBox.findText(text[0]) == -1):
                        QMessageBox.warning(self,"Error","Invalid station")
                        return False
                    else:
                        # updates corresponding dropdown and caches new value
                        self.update = False
                        self.Station_comboxBox.setCurrentIndex(self.Station_comboxBox.findText(text[0]))
                        self.District_comboBox.setCurrentIndex(-1)
                        self.Suburb_comboBox.setCurrentIndex(-1)
                        self.Region_comboBox.setCurrentIndex(-1)
                        self.cache_zone = self.Station_comboxBox.currentText()
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
                        self.Station_comboxBox.setCurrentIndex(-1)
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
                        self.Station_comboxBox.setCurrentIndex(-1)
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
                        self.Station_comboxBox.setCurrentIndex(-1)
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
        else:
            return False

    # Function for Screenshot button    
    def screenshot(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                "Save Image",
                                                                "./",  # initial dir
                                                                ".jpg")

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.frame.winId())
        screenshot.save(fileName_choose, 'jpg')
        
    ##################################### Layout Events ###############################################
    def initDrag(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        # set mouse tracking
        self._move_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self._left_drag = False
        self._right_bottom_corner_drag = False
        self._left_bottom_corner_drag = False
        self.minWidth = 903
    
    def resizeEvent(self, QResizeEvent):
        # Resize border area 
        self._left_rect = [QPoint(x, y) for x in range(0, 5)
                           for y in range(5, self.height() - 5)]
        self._right_rect = [QPoint(x, y) for x in range(self.width() - 5, self.width() + 1)
                           for y in range(5, self.height() - 5)]
        self._bottom_rect = [QPoint(x, y) for x in range(5, self.width() - 5)
                         for y in range(self.height() - 5, self.height() + 1)]
        self._right_bottom_corner_rect = [QPoint(x, y) for x in range(self.width() - 5, self.width() + 1)
                                    for y in range(self.height() - 5, self.height() + 1)]
        self._left_bottom_corner_rect = [QPoint(x, y) for x in range(0, 5)
                             for y in range(self.height() - 5, self.height() + 1)]

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton) and (event.pos() in self._right_bottom_corner_rect):
            self._right_bottom_corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._left_bottom_corner_rect):
            self._left_bottom_corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._left_rect):
            self._left_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.groupBox.height()):
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if self.isMaximized():
            pass
        else:
            if QMouseEvent.pos() in self._right_bottom_corner_rect:
                self.setCursor(Qt.SizeFDiagCursor)
            elif QMouseEvent.pos() in self._left_bottom_corner_rect:
                self.setCursor(Qt.SizeBDiagCursor)
            elif QMouseEvent.pos() in self._bottom_rect:
                self.setCursor(Qt.SizeVerCursor)
            elif QMouseEvent.pos() in self._right_rect:
                self.setCursor(Qt.SizeHorCursor)
            elif QMouseEvent.pos() in self._left_rect:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            if Qt.LeftButton and self._right_drag:
                self.resize(QMouseEvent.pos().x(), self.height())
                QMouseEvent.accept()
            elif Qt.LeftButton and self._left_drag:
                if self.width() - QMouseEvent.pos().x() > self.minWidth:
                    self.resize(self.width() - QMouseEvent.pos().x(), self.height())
                    self.move(self.x() + QMouseEvent.pos().x(), self.y())
                QMouseEvent.accept()
            elif Qt.LeftButton and self._bottom_drag:
                self.resize(self.width(), QMouseEvent.pos().y())
                QMouseEvent.accept()
            elif Qt.LeftButton and self._right_bottom_corner_drag:
                self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
                QMouseEvent.accept()
            elif Qt.LeftButton and self._left_bottom_corner_drag:
                if self.width() - QMouseEvent.pos().x() > self.minWidth:
                    self.resize(self.width() - QMouseEvent.pos().x(), QMouseEvent.pos().y())
                    self.move(self.x() + QMouseEvent.pos().x(), self.y())
                QMouseEvent.accept()
            elif Qt.LeftButton and self._move_drag:
                self.move(QMouseEvent.globalPos() - self.move_DragPosition)
                QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self._move_drag = False
        self._right_bottom_corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self._left_drag = False
        self._left_bottom_corner_drag = False
    ##################################### End of Layout Events ###############################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())