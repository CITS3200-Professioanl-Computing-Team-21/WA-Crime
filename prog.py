import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets, QtCore
from ui import Ui_MainWindow
import boundaries
import csv, sqlite3, os, pandas
import numpy as np
import pandas as pd
import json
import haversine as hs
from fuzzywuzzy import process
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from os.path import join
import geopandas as gpd
from geopy.geocoders import Nominatim
import folium
# from PyQt5 import QtCore, QtGui, QtWidgets

# BUTTON IDENTIFIERS
STATION = 0
DISTRICT = 1
REGION = 2
YEAR = 3
MONTH = 4
QUARTER = 5
CRIME = 6
SUBURB = 7

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.showHtml()
        self.Search_pushButton.clicked.connect(self.query)
        self.Screenshot_pushButton.clicked.connect(self.screenshot)

        # initalises combo boxes options from csv in ./config
        self.Station_comboxBox.addItems(self.readfile("stations.csv"))
        self.District_comboBox.addItems(self.readfile("districts.csv"))
        self.Region_comboBox.addItems(self.readfile("regions.csv"))
        self.Suburb_comboBox.addItems(self.readfile("suburbs.csv"))
        self.Year_comboBox_1.addItems(self.readfile("years.csv"))
        self.Year_comboBox_2.addItems(self.readfile("years.csv"))
        MONTHS = ['All','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun']
        self.Monthly_comboBox_1.addItems(MONTHS)
        self.Monthly_comboBox_2.addItems(MONTHS)
        QUARTERS = ['All','Q3','Q4','Q1','Q2']
        self.Quarterly_comboBox_1.addItems(QUARTERS)
        self.Quarterly_comboBox_2.addItems(QUARTERS)
        self.Crime_comboBox.addItems(self.readfile("crime_types.csv"))

        # inital configuration
        self.cache_zone_type = "Region"
        self.cache_zone = "All"
        self.cache_year = "All"
        self.cache_period = "All"
        self.cache_crime = "All"
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
        self.Year_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(YEAR))
        self.Monthly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(MONTH))
        self.Monthly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(MONTH))
        self.Quarterly_comboBox_1.currentIndexChanged.connect(lambda : self.generate_map(QUARTER))
        self.Quarterly_comboBox_2.currentIndexChanged.connect(lambda : self.generate_map(QUARTER))

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
                self.cache_zone_type = "Station"
                self.cache_zone = self.Station_comboxBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == DISTRICT:
                self.cache_zone_type = "District"
                self.cache_zone = self.District_comboBox.currentText()
                self.update = False
                self.Station_comboxBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == REGION:
                self.cache_zone_type = "Region"
                self.cache_zone = self.Region_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboxBox.setCurrentIndex(-1)
                self.Suburb_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == SUBURB:
                self.cache_zone_type = "Suburb"
                self.cache_zone = self.Suburb_comboBox.currentText()
                self.update = False
                self.District_comboBox.setCurrentIndex(-1)
                self.Station_comboxBox.setCurrentIndex(-1)
                self.Region_comboBox.setCurrentIndex(-1)
                self.update = True
            elif src == QUARTER:
                self.cache_period = self.Quarterly_comboBox_1.currentText()
                if self.Quarterly_comboBox_2.currentIndex() != -1:
                    self.cache_period += "-"+self.Quarterly_comboBox_2.currentText()
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(-1)
                self.Monthly_comboBox_2.setCurrentIndex(-1)
                self.update = True
            elif src == MONTH:
                self.cache_period = self.Monthly_comboBox_1.currentText()
                if self.Monthly_comboBox_2.currentIndex() != -1:
                    self.cache_period += "-"+self.Monthly_comboBox_2.currentText()
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(-1)
                self.Quarterly_comboBox_2.setCurrentIndex(-1)
                self.update = True
            elif src == YEAR:
                self.cache_year = self.Year_comboBox_1.currentText()
                if self.Year_comboBox_2.currentIndex() != -1:
                    self.cache_year += "-"+self.Year_comboBox_2.currentText()
            elif src == CRIME:
                self.cache_crime = self.Crime_comboBox.currentText()

            # generates new html (placeholder for front end)
            self.stub(self.cache_zone, self.cache_zone_type, self.cache_year, self.cache_period, self.cache_crime)

            # updates html display with new html
            url = QtCore.QUrl.fromLocalFile("/trial.html")
            self.browser.load(url)

    # placeholder, function generates a html based on input query
    def stub(self,name, zone_type, year, period, crime):
        print("Name, Zone_type, Year, Period, Crime")
        print(name, zone_type, year, period, crime)
        output = boundaries.chloropleth([name, zone_type, year, period, crime])

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
    def query(self):
        text = self.Search_Box.text().split()
        print(text)
        # check num args
        if (len(text) != 5):
            print("invalid number of args")
            return False
        
        # checking zone
        if (text[1] not in ["Station","District","Region","Suburb"]):
            print("invalid Zone")
            return False
        else:
            if text[1] == "Station":
                if (self.Station_comboxBox.findText(text[0]) == -1):
                    print("invalid Station")
                    return False
                else:
                    self.update = False
                    self.Station_comboxBox.setCurrentIndex(self.Station_comboxBox.findText(text[0]))
                    self.update = True
            elif text[1] == "District":
                if (self.District_comboBox.findText(text[0]) == -1):
                    print("invalid District")
                    return False
                else:
                    self.update = False
                    self.District_comboBox.setCurrentIndex(self.District_comboBox.findText(text[0]))
                    self.update = True
            elif text[1] == "Region":
                if (self.Region_comboBox.findText(text[0]) == -1):
                    print("invalid Region")
                    return False
                else:
                    self.update = False
                    self.Region_comboBox.setCurrentIndex(self.Suburb_comboBox.findText(text[0]))
                    self.update = True
            elif text[1] == "Suburb":
                if (self.Suburb_comboBox.findText(text[0]) == -1):
                    print("invalid Suburb")
                    return False
                else:
                    self.update = False
                    self.Suburb_comboBox.setCurrentIndex(self.Suburb_comboBox.findText(text[0]))
                    self.update = True
        
        ''' #waiting on specifications before implementing error checking
        # check year
        if (self.Year_comboBox_1.findText(text[2]) == -1):
            print("invalid Year")
            return False
        else:
            self.update = False
            self.Year_comboBox_1.setCurrentIndex(self.Year_comboBox_1.findText(text[2]))
            self.update = True

        #check month/quarter
        if (self.Monthly_comboBox_1.findText(text[3]) == -1):
            if (self.Quarterly_comboBox_1.findText(text[3]) == -1):
                print("invalid number of Period")
                return False
            else:
                self.update = False
                self.Quarterly_comboBox_1.setCurrentIndex(self.Quarterly_comboBox_1.findText(text[3]))
                self.update = True
        else:
                self.update = False
                self.Monthly_comboBox_1.setCurrentIndex(self.Monthly_comboBox_1.findText(text[3]))
                self.update = True
        '''
        # check crime
        if (self.Crime_comboBox.findText(text[4]) == -1):
            print("invalid number of Crime")
            return False
        else:
            self.update = False
            self.Crime_comboBox.setCurrentIndex(self.Crime_comboBox.findText(text[4]))
            self.update = True

        # generates new html (placeholder for front end)
        self.stub(text[0], text[1], text[2], text[3], text[4])

        # updates html display with new html
        url = QtCore.QUrl.fromLocalFile("/trial.html")
        self.browser.load(url)
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

DATA = 'crime.csv'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'Suburb Locality.csv'
files = [DATA, LANDGATE, ZONES]

# function - to check if required files exist
def check_file(file):
    if not os.path.isfile(file): 
        return None
    else:
        return True

# function - to extract data from datafiles and intiate cleaning
def data_loading(crime, landgate, zones):
    with open(LANDGATE) as f:
        landgate_data = json.load(f)
        landgate_locations = [i['properties']['name'].lower() for i in landgate_data['features']]

    crime_data = pd.read_csv(crime)
    # selects all unique string values from first column and converts to lowercase, output = array
    crime_locations = np.char.lower(crime_data.iloc[:, 0].unique().astype('str'))
    
    # reads dataframe, converts all values to string and lowercase
    zones_data = pd.read_csv(zones).apply(lambda x: x.astype(str).str.lower())
    zones_data.columns = ['suburbs', 'stations', 'districts', 'regions']
    # converts dataframe into a dictionary where each key, value pair = 'column name': [column values as a list]
    zones = zones_data.to_dict(orient="list")
    for i in zones:
        zones[i] = np.unique(np.array(zones[i]))
    return (landgate_data, landgate_locations, crime_locations, zones_data, zones)

def check_naming(landgate_locations, crime_locations, zones):
    for location in crime_locations:
        missing1 = [location for location in crime_locations if location not in zones['suburbs']]
        missing2 = [location for location in crime_locations if location not in landgate_locations]
    changes = []
    if not missing1:
        if missing2: 
            for location in missing2:
                highest = process.extractOne(location, landgate_locations)
                landgate_location, score = highest[0], highest[1]
                if landgate_location not in crime_locations and score > 85:
                    changes.append((location, landgate_location))
                    missing2.remove(location)
    return (missing2, changes)

def missing_locations(zones_data, zones, missing2):
    station_coordinates = {}
    for station in zones['stations']:
        # calling the Nominatim tool
        loc = Nominatim(user_agent="GetLoc") 
        # entering the location name
        getLoc = loc.geocode(station+', WA, Australia')
        station_coordinates[station] = (getLoc.latitude, getLoc.longitude)
    missing_landgate = {}
    for location in missing2:
        # calling the Nominatim tool
        loc = Nominatim(user_agent="GetLoc") 
        # entering the location name
        getLoc = loc.geocode(location+', WA, Australia')
        if getLoc:
            missing_point = (getLoc.latitude, getLoc.longitude)
            station_name = zones_data.loc[zones_data['suburbs'] == location, 'stations'].item()
            station_coordinate = station_coordinates[station_name]
            if hs.haversine(missing_point, station_coordinate) <= 200:
                missing_landgate[location] = missing_point
            else: print('>200', location)
        else : print('not found', location)
    return (missing_landgate)

def assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations):
    for location in missing_landgate:
        point = Point(missing_landgate[location][1], missing_landgate[location][0])
        for i in landgate_data['features']:
            polygon = shape(i['geometry'])
            landgate_location = i['properties']['name'].lower()
            if polygon.contains(point) and landgate_location not in crime_locations:
                changes.append((location, landgate_location))
    return (changes)

def zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations, zones_data):
    final_data = {'suburbs': {}, 'stations': {}, 'districts': {}, 'regions': {}}
    for zone_type in zones:
        if zone_type != 'suburbs':
            for location in zones[zone_type]:
                boundary_locations = list(zones_data.loc[zones_data[zone_type] == location, 'suburbs'])
                boundary_locations_landgate = []
                for i in boundary_locations:
                    if i in landgate_locations:
                        boundary_locations_landgate.append(i)
                final_data[zone_type][location] = boundary_locations_landgate
        
    for location in landgate_data['features']:
        name = location['properties']['name'].lower()
        if name in zones['suburbs']:
            final_data['suburbs'][name] = location['geometry']
                    
    for zone_type in final_data:
        if zone_type != 'suburbs':
            for place in final_data[zone_type]:
                polygons = []
                for location in final_data[zone_type][place]:
                    polygons.append(shape(final_data['suburbs'][location]))
                boundary = gpd.GeoSeries(unary_union(polygons).simplify(tolerance=0.001))
                final_data[zone_type][place] = boundary.to_json()

    return(final_data)

def chloropleth(query):
    # results = mp.main(query)
    # print(results)
    print(query[0], query[1], query[2], query[3], query[4])
    results = filter(query[0], query[1], query[2], query[3], query[4])
    results['name'] = results['name'].str.upper()
    results['log'] = np.log(results['sum']+1)

    #Creating a map object for choropleth map
    #Starting location coordinates [lat, long] set to Perth
    chloropleth = folium.Map(
        location=[-32, 116],
        tiles='https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        zoom_start=12,
        attr='Trial Heatmap')

    #Creating choropleth map object with key on suburb name
    folium.Choropleth(
        geo_data = LANDGATE, #Assign geo_data to your geojson file
        name = "WA Crime Heat Map",
        data = results, #Assign dataset of interest
        columns = ['name', 'log'], #Assign columns in the dataset for plotting
        key_on = 'feature.properties.name', #Assign the key that geojson uses to connect with dataset
        fill_color = 'YlOrRd',
        fill_opacity = 0.9,
        line_opacity = 0.5,
        bins = 9,
        legend_name = 'legend').add_to(chloropleth)
    
    #Creating style_function
    style_function = lambda x: {
                    'fillColor': '#ffffff', 
                    'color':'#000000', 
                    'fillOpacity': 0.1, 
                    'weight': 0.1}

    #Creating highlight_function
    highlight_function = lambda x: {
                    'fillColor': '#000000', 
                    'color':'#000000', 
                    'fillOpacity': 0.50, 
                    'weight': 0.1}

    #Creating popup tooltip object
    NIL = folium.features.GeoJson(
        LANDGATE,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name'],
            aliases=['name'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    #Adding tooltip object to the map
    chloropleth.add_child(NIL)
    chloropleth.keep_in_front(NIL)
    folium.LayerControl().add_to(chloropleth)

    chloropleth.save('trial.html')
    
def main2():
    for file in files:
        if check_file(file) == None:
            return None
    # landgate_data, landgate_locations, crime_locations, zones_data, zones = data_loading(DATA, LANDGATE, ZONES)
    # missing2, changes = check_naming(landgate_locations, crime_locations, zones)
    # missing_landgate = missing_locations(zones_data, zones, missing2)
    # changes = assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations)
    # final_data = zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations, zones_data)
    query = ["Mandurah", "Station", "2012-2013-2015-2016", "Jul-Oct", "Stealing"]
    chloropleth(query)
    # return final_data

# if __name__ == '__main__':
#     main()

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled1.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1614, 816)
        MainWindow.setStyleSheet("font:20px\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(350, 50))
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.Search_pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Search_pushButton.sizePolicy().hasHeightForWidth())
        self.Search_pushButton.setSizePolicy(sizePolicy)
        self.Search_pushButton.setMinimumSize(QtCore.QSize(110, 50))
        self.Search_pushButton.setObjectName("Search_pushButton")
        self.horizontalLayout.addWidget(self.Search_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_10 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_2.addWidget(self.label_10)
        spacerItem = QtWidgets.QSpacerItem(420, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_3.addWidget(self.label_9)
        self.Crime_comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Crime_comboBox.sizePolicy().hasHeightForWidth())
        self.Crime_comboBox.setSizePolicy(sizePolicy)
        self.Crime_comboBox.setMinimumSize(QtCore.QSize(370, 41))
        self.Crime_comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Crime_comboBox.setObjectName("Crime_comboBox")
        self.horizontalLayout_3.addWidget(self.Crime_comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_18 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy)
        self.label_18.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_18.setFont(font)
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_4.addWidget(self.label_18)
        spacerItem1 = QtWidgets.QSpacerItem(420, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.Region_comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Region_comboBox.sizePolicy().hasHeightForWidth())
        self.Region_comboBox.setSizePolicy(sizePolicy)
        self.Region_comboBox.setMinimumSize(QtCore.QSize(370, 41))
        self.Region_comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Region_comboBox.setObjectName("Region_comboBox")
        self.horizontalLayout_5.addWidget(self.Region_comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.District_comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.District_comboBox.sizePolicy().hasHeightForWidth())
        self.District_comboBox.setSizePolicy(sizePolicy)
        self.District_comboBox.setMinimumSize(QtCore.QSize(370, 41))
        self.District_comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.District_comboBox.setObjectName("District_comboBox")
        self.horizontalLayout_6.addWidget(self.District_comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_7.addWidget(self.label_2)
        self.Station_comboxBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Station_comboxBox.sizePolicy().hasHeightForWidth())
        self.Station_comboxBox.setSizePolicy(sizePolicy)
        self.Station_comboxBox.setMinimumSize(QtCore.QSize(370, 41))
        self.Station_comboxBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Station_comboxBox.setObjectName("Station_comboxBox")
        self.horizontalLayout_7.addWidget(self.Station_comboxBox)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_14 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_8.addWidget(self.label_14)
        self.Suburb_comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Suburb_comboBox.sizePolicy().hasHeightForWidth())
        self.Suburb_comboBox.setSizePolicy(sizePolicy)
        self.Suburb_comboBox.setMinimumSize(QtCore.QSize(370, 41))
        self.Suburb_comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Suburb_comboBox.setObjectName("Suburb_comboBox")
        self.horizontalLayout_8.addWidget(self.Suburb_comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_19 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        self.label_19.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_19.setFont(font)
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_9.addWidget(self.label_19)
        spacerItem2 = QtWidgets.QSpacerItem(420, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_20 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        self.label_20.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_10.addWidget(self.label_20)
        spacerItem3 = QtWidgets.QSpacerItem(115, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem3)
        self.Year_comboBox_1 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Year_comboBox_1.sizePolicy().hasHeightForWidth())
        self.Year_comboBox_1.setSizePolicy(sizePolicy)
        self.Year_comboBox_1.setMinimumSize(QtCore.QSize(70, 41))
        self.Year_comboBox_1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Year_comboBox_1.setObjectName("Year_comboBox_1")
        self.horizontalLayout_10.addWidget(self.Year_comboBox_1)
        self.label_15 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)
        self.label_15.setMinimumSize(QtCore.QSize(30, 0))
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_10.addWidget(self.label_15)
        self.Year_comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Year_comboBox_2.sizePolicy().hasHeightForWidth())
        self.Year_comboBox_2.setSizePolicy(sizePolicy)
        self.Year_comboBox_2.setMinimumSize(QtCore.QSize(70, 41))
        self.Year_comboBox_2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Year_comboBox_2.setObjectName("Year_comboBox_2")
        self.horizontalLayout_10.addWidget(self.Year_comboBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_21 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy)
        self.label_21.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.horizontalLayout_12.addWidget(self.label_21)
        spacerItem4 = QtWidgets.QSpacerItem(115, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem4)
        self.Monthly_comboBox_1 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Monthly_comboBox_1.sizePolicy().hasHeightForWidth())
        self.Monthly_comboBox_1.setSizePolicy(sizePolicy)
        self.Monthly_comboBox_1.setMinimumSize(QtCore.QSize(70, 41))
        self.Monthly_comboBox_1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Monthly_comboBox_1.setObjectName("Monthly_comboBox_1")
        self.horizontalLayout_12.addWidget(self.Monthly_comboBox_1)
        self.label_16 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setMinimumSize(QtCore.QSize(30, 0))
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_12.addWidget(self.label_16)
        self.Monthly_comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Monthly_comboBox_2.sizePolicy().hasHeightForWidth())
        self.Monthly_comboBox_2.setSizePolicy(sizePolicy)
        self.Monthly_comboBox_2.setMinimumSize(QtCore.QSize(70, 41))
        self.Monthly_comboBox_2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Monthly_comboBox_2.setObjectName("Monthly_comboBox_2")
        self.horizontalLayout_12.addWidget(self.Monthly_comboBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_22 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_22.sizePolicy().hasHeightForWidth())
        self.label_22.setSizePolicy(sizePolicy)
        self.label_22.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_13.addWidget(self.label_22)
        spacerItem5 = QtWidgets.QSpacerItem(115, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem5)
        self.Quarterly_comboBox_1 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Quarterly_comboBox_1.sizePolicy().hasHeightForWidth())
        self.Quarterly_comboBox_1.setSizePolicy(sizePolicy)
        self.Quarterly_comboBox_1.setMinimumSize(QtCore.QSize(70, 41))
        self.Quarterly_comboBox_1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Quarterly_comboBox_1.setObjectName("Quarterly_comboBox_1")
        self.horizontalLayout_13.addWidget(self.Quarterly_comboBox_1)
        self.label_17 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy)
        self.label_17.setMinimumSize(QtCore.QSize(30, 0))
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_13.addWidget(self.label_17)
        self.Quarterly_comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Quarterly_comboBox_2.sizePolicy().hasHeightForWidth())
        self.Quarterly_comboBox_2.setSizePolicy(sizePolicy)
        self.Quarterly_comboBox_2.setMinimumSize(QtCore.QSize(70, 41))
        self.Quarterly_comboBox_2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Quarterly_comboBox_2.setObjectName("Quarterly_comboBox_2")
        self.horizontalLayout_13.addWidget(self.Quarterly_comboBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_13)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem6)
        self.frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(800, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_12 = QtWidgets.QLabel(self.widget)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_18.addWidget(self.label_12)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_18.addItem(spacerItem7)
        self.verticalLayout_3.addLayout(self.horizontalLayout_18)
        self.frame_2 = QtWidgets.QFrame(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(300, 260))
        self.frame_2.setStyleSheet("background-color:white")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_3.addWidget(self.frame_2)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.line_8 = QtWidgets.QFrame(self.widget)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.verticalLayout_4.addWidget(self.line_8)
        self.verticalLayout_6.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.label_13 = QtWidgets.QLabel(self.widget)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_19.addWidget(self.label_13)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_19.addItem(spacerItem8)
        self.verticalLayout_5.addLayout(self.horizontalLayout_19)
        self.frame_3 = QtWidgets.QFrame(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMinimumSize(QtCore.QSize(300, 260))
        self.frame_3.setStyleSheet("background-color:white")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_5.addWidget(self.frame_3)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.line_9 = QtWidgets.QFrame(self.widget)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.verticalLayout_6.addWidget(self.line_9)
        spacerItem9 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem9)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem10 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem10)
        spacerItem11 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem11)
        spacerItem12 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem12)
        self.verticalLayout_6.addLayout(self.horizontalLayout_11)
        spacerItem13 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_6.addItem(spacerItem13)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        spacerItem14 = QtWidgets.QSpacerItem(37, 38, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_20.addItem(spacerItem14)
        self.Screenshot_pushButton = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Screenshot_pushButton.sizePolicy().hasHeightForWidth())
        self.Screenshot_pushButton.setSizePolicy(sizePolicy)
        self.Screenshot_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.Screenshot_pushButton.setObjectName("Screenshot_pushButton")
        self.horizontalLayout_20.addWidget(self.Screenshot_pushButton)
        spacerItem15 = QtWidgets.QSpacerItem(37, 38, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_20.addItem(spacerItem15)
        self.verticalLayout_6.addLayout(self.horizontalLayout_20)
        spacerItem16 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem16)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Map"))
        self.Search_pushButton.setText(_translate("MainWindow", "Search"))
        self.label_10.setText(_translate("MainWindow", "Crime"))
        self.label_9.setText(_translate("MainWindow", "Type"))
        self.label_18.setText(_translate("MainWindow", "Zone"))
        self.label_4.setText(_translate("MainWindow", "Region"))
        self.label_3.setText(_translate("MainWindow", "District"))
        self.label_2.setText(_translate("MainWindow", "Station"))
        self.label_14.setText(_translate("MainWindow", "Suburb"))
        self.label_19.setText(_translate("MainWindow", "Time"))
        self.label_20.setText(_translate("MainWindow", "Year Range"))
        self.label_15.setText(_translate("MainWindow", "-"))
        self.label_21.setText(_translate("MainWindow", "Monthly"))
        self.label_16.setText(_translate("MainWindow", "-"))
        self.label_22.setText(_translate("MainWindow", "Quarterly"))
        self.label_17.setText(_translate("MainWindow", "-"))
        self.label_12.setText(_translate("MainWindow", "Frame 1"))
        self.label_13.setText(_translate("MainWindow", "Frame 2"))
        self.Screenshot_pushButton.setText(_translate("MainWindow", "Export"))

# Desktop (windows) works for relative addresses for some reason, Mac doesn't
# Desktop location: C:/Users/User/OneDrive/Uni/CITS3200/WA-Crime/data.db
# Mac location /Users/blank/OneDrive/Uni/CITS3200/WA-Crime/data.db

def filter(name, zone, year, mq, offence):

    # Stupid inconsistency between files
    year = year.lower()
    if mq == 'All':
        mq = mq.lower()
    elif mq[0] == "-":
        mq = mq[1:]
    offence = offence.lower()
    name = name.lower()
    database = "data.db"
    crime_file = "crime.csv"
    localities_file = "localities.csv"

    # Year_fn is financial year starting year. Do not need to store the
    # following year - it is implied. Use of integer makes for easier
    # comparison.
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS Crime (
                                        Suburb text NOT NULL,
                                        Crime text NOT NULL,
                                        Year_fn int NOT NULL,
                                        Jul int,
                                        Aug int,
                                        Sep int,
                                        Oct int,
                                        Nov int,
                                        Dec int,
                                        Jan int,
                                        Feb int,
                                        Mar int,
                                        Apr int,
                                        May int,
                                        Jun int,
                                        Annual int
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS Localities (
                                    Suburb text PRIMARY KEY NOT NULL,
                                    Station text NOT NULL,
                                    District text NOT NULL,
                                    Region text NOT NULL
                                );"""

    # Create a database connection
    conn = create_connection(database)

    # Create tables if they don't exist, create cursor
    if conn is not None:
        c = conn.cursor()
        # Create data table
        filled = create_table(c, sql_create_projects_table, "Crime")
        # Only fill tables if no data in them - avoids redundantly doing
        # it each time.
        if not filled:
            fill_table(c, crime_file, "Crime")
        conn.commit()

        # Create localities table
        filled = create_table(c, sql_create_tasks_table, "Localities")
        if not filled:
            fill_table(c, localities_file, "Localities")
        conn.commit()
    else:
        print("Error! cannot create the database connection.")
        return
    
    # Build query in stages
    query = ""
    mrange = ""
    y1, y2 = 0, 0
    
    print(mq)

    if str(mq).find('all') == -1:
        # If it is a single month entry, i.e. no - found, mrange is just that one month
        mrange = str(distribution(mq))
    else:
        # We assume no more updates to the calendar system
        mq = "Jul-Jun"
        mrange = str(distribution(mq))

    # If there is an 'all' type input assume all year range.
    # print(year)
    if str(year).find('all') == -1:
        y1, y2 = yrange(year)
    else:
        # In-built Y3K bug
        y1, y2 = "0", "3000"
    # If year order came in the wrong way
    if y1 > y2:
        y2, y1 = y1, y2
    # query += "SELECT " + zone + ", " + mrange + " AS Total FROM Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb"
    # query += "SELECT Crime." + zone + ", " + mrange + " AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb) WHERE Crime.Suburb = '" + name + "'"
    
    # Determines subordinate zone type for selection and grouping (This feature may be made redundant in the future in favour of a custom zone selection)
    zones = ['Suburb', 'Station', 'District', 'Region']
    sub_zone = ""

    # All selection for zone defaults to suburb, also resets sub_zone and name to 'all' so that all suburbs are selected.
    if zone == 'all' or zone == 'Suburb':
        zone = 'Suburb'
        sub_zone = 'Suburb'
        name = 'all'

    # When name is 'all', we return all of that zone type, therefore no subzones. When name is not all, we return only the named zone and it's subzones.
    if name != 'all':
        sub_zone = zones[zones.index(zone) - 1]
    else:
        sub_zone = zone

    # Below is for a more descriptive query result
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"

    print(y1, y2, sub_zone, zone, mrange, offence, name)

    query += "SELECT Localities." + sub_zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"
    # CURRENT PROBLEM. LEAKS AROUND YEAR_FN REQUIRING YOU INCLUDE PREVIOUS OR FOLLOWING YEARS
    if name != 'all' or offence != 'all' or year != 'all':
        query += " WHERE"
        # includeand to check if query has multiple conditions, so that "AND" can be appended to include them
        includeand = False
        if name != 'all':
            query += " Localities." + zone + " = '" + name.lower() + "'"
            includeand = True
        if offence != 'all':
            if includeand:
                query += " AND"
            query += " Crime = '" + offence.lower() + "'"
            includeand = True
        if year != 'all':
            if includeand:
                query += " AND"
            query += " Year_fn >= " + y1 + " AND Year_fn < " + y2
    # if sub_zone == 'Suburb':
    #     query += " GROUP BY Year_fn, Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # else:
    #     query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    # Don't group by year
    if sub_zone == 'Suburb':
        query += " GROUP BY Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    else:
        query += " GROUP BY " + sub_zone + " ORDER BY " + sub_zone

    # # All crime type all year type
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"
    # # CURRENT PROBLEM. YEAR_FN IS ISNT PROPERLY INT FORM, CANT DO COMPARISON 
    # query += " WHERE Localities." + zone + " = '" + name.lower() + "'"
    # query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    print(query)
    
    # Print output to command line
    c.execute(query)
    j = 0
    output = []
    for i in c.fetchall():
        output.append(list(i))
        # print(j, i)
        j += 1
    # print(c.fetchall())

    # print(query)
    output = convert(output)
    # print(output)
    return output

def distribution(mq):
    # Collects the months whose data are to be summed, scans from m0 to m1 collecting
    # months in between.
    months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    query = ""
    if mq != 'all':
        # Quarters not done yet
        mrange = "("
        # if mq[0] == 'q':
        #     if str(mq).find("-") != -1:
        #         mq = mq.split("-")

        mq = str(mq).split("-")

        # Check if it is a range, meaning split by - was successful
        if len(mq) > 1:

            if mq[0][0] == 'Q':
                # Calculate starting month
                mq[0] = months[(int(mq[0][1])-1)*3]
                mq[1] = months[(int(mq[1][1]))*3-1]

            m0 = mq[0]
            m1 = mq[1]
            mi = months.index(m0)
            curr = m0
            while curr != m1:
                mrange += curr + "+"
                # If Sep-Aug we modulo past Dec until we reach Aug
                mi = (mi + 1) % 12
                curr = months[mi]
            # Closes the range with bracket
            mrange += curr + ')'
            # print(mrange)
            return mrange
        else:
            # Assuming no months will ever start with Q
            if mq[0][0] == 'Q':
                # Calculate starting month
                start = months[(int(mq[0][1])-1)*3]
                mi = months.index(start)
                end = months[int(mq[0][1])*3-1]
                while start != end:
                    mrange += start + "+"
                    # If Sep-Aug we modulo past Dec until we reach Aug
                    mi = (mi + 1) % 12
                    start = months[mi]
                mrange += start + ')'
                return mrange
            else:
                return mq[0]
            

        # m0 = mq[0:3]
        # # Index of first month so we can iterate through list
        # mi = months.index(m0)
        # m1 = mq[4:]
        # curr = m0


# May be buggy for weird inputs like 'all-2013-2014' or '2013-2014-all' or 'all-all'
def yrange(year):
    y = year.split('-')
    # print(y)
    # Stupid selector input difference has me doing this stupidness. Format for end year 2021 is '21', so I need to infer the century and add 21 to it to get the year I want '2021'
    return y[0], str(int(int(y[-2])/100)) + y[-1]

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print("Connect to database error") 
    return conn

def create_table(c, create_table_sql, table):
    try:
        # Only create table if it doesn't exist (data can't be accessed)
        try:
            # LIMIT 1 just to make the selection quick if table does exist.
            query = "SELECT * FROM " + table + " LIMIT 1"
            c.execute(query)
            # Return true to indicate table exists and has data, no need to fill it again.
            # print(c.rowcount)
            if len(c.fetchall()) > 0:
                return True
            return False
        except:
            c.execute(create_table_sql)
            return False
    except:
        print("Create table error")
        return None

# This shit isn't working for some reason. NOW IT IS
def fill_table(c, file_name, table):
    try:
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            columns = next(reader)
            query = "INSERT INTO " + table + " VALUES({})".format(','.join('?' * len(columns)))
            for data in reader:
                # Also converts everything to lower case
                data = [e.lower() for e in data]
                # Turn year_fn into an int that is just the beginning year. 
                if table == "Crime":
                    data[2] = int(data[2].split("-")[0])
                c.execute(query, data)
            c.commit()
    except:
        print("Error filling table data")
    
# Converts list to pandas data frame    
def convert(list):
    df = pandas.DataFrame(list, columns = ['name', 'sum'])
    return df


# Name, zone, year, month/quarter, crime
# filter('Mandurah', 'Station', 'all-2016-2017', 'Jul-Oct', 'Stealing') 

#perth district = 92571, wembley station = 34120



