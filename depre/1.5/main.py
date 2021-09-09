import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from Application_Bo import Ui_MainWindow

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.setting()
        self.showHtml()
        self.search_pushButton_2.clicked.connect(self.back)
        self.spinBox.valueChanged.connect(self.change_table)
        self.Screenshot_pushButton.clicked.connect(self.screenshot)

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
    
    # Config for selector dropdown, Initalises combo boxes
    def setting(self):
        self.station = ['albany', 'armadale', 'augusta', 'australian federal police', 'australind', 'balgo',
                        'ballajura', 'bayswater', 'belmont', 'bencubbin', 'beverley', 'bidyadanga', 'blackstone',
                        'boddington', 'boyup brook', 'bridgetown', 'brookton', 'broome', 'bruce rock', 'bunbury',
                        'burringurrah', 'busselton', 'canning vale', 'cannington', 'capel', 'carnamah', 'carnarvon',
                        'clarkson', 'cockburn', 'collie', 'coolgardie', 'corrigin', 'cranbrook', 'cue', 'cunderdin',
                        'dalwallinu', 'dampier', 'dampier peninsula', 'denmark', 'derby', 'dongara', 'donnybrook',
                        'dowerin', 'dumbleyung', 'dunsborough', 'dwellingup', 'ellenbrook', 'esperance', 'eucla',
                        'exmouth', 'fitzroy crossing', 'forrestfield', 'fremantle', 'gascoyne junction', 'geraldton',
                        'gingin', 'gnowangerup', 'goomalling', 'gosnells', 'halls creek', 'harvey', 'hillarys',
                        'hopetoun', 'jerramungup', 'jigalong', 'joondalup', 'jurien bay', 'kalbarri', 'kalgoorlie',
                        'kalumburu', 'kambalda', 'karratha', 'katanning', 'kellerberrin', 'kensington', 'kiara', 'kintore',
                        'kojonup', 'kondinin', 'koorda', 'kulin', 'kununurra', 'kwinana', 'lake grace', 'lancelin',
                        'laverton', 'leeman', 'leinster', 'leonora', 'looma', 'mandurah', 'manjimup', 'marble bar',
                        'margaret river', 'meekatharra', 'menzies', 'merredin', 'midland', 'mingenew', 'mirrabooka',
                        'moora', 'morawa', 'morley', 'mount barker', 'mount magnet', 'mukinbudin', 'mullewa', 'mundaring',
                        'mundijong', 'murdoch', 'nannup', 'narembeen', 'narrogin', 'newman', 'norseman', 'northam', 'northampton',
                        'nullagine', 'onslow', 'palmyra', 'pannawonica', 'paraburdoo', 'pemberton', 'perenjori', 'perth',
                        'pingelly', 'pinjarra', 'port hedland', 'quairading', 'ravensthorpe', 'rockingham', 'roebourne',
                        'rottnest', 'scarborough', 'shark bay', 'south hedland', 'southern cross', 'tambellup', 'three springs',
                        'tom price', 'toodyay', 'unknown', 'wagin', 'walpole', 'wanneroo', 'warakurna', 'warburton',
                        'warmun', 'waroona', 'warwick', 'wembley', 'wickepin', 'williams', 'wiluna', 'wongan hills',
                        'wundowie', 'wyalkatchem', 'wyndham', 'yalgoo', 'yanchep', 'yarloop', 'york']

        self.district =  ['armadale', 'cannington', 'external agency access', 'fremantle', 'goldfields-esperance', 'great southern',
                          'joondalup', 'kimberley', 'mandurah', 'mid west-gascoyne', 'midland', 'mirrabooka', 'perth', 'pilbara',
                          'south west', 'unknown', 'wheatbelt']

        self.region = ['metropolitan region north', 'metropolitan region south', 'regional wa region', 'rmis business unit', 'unknown']

        self.crime = ['arson', 'assault (family)', 'assault (non-family)', 'breach of violence restraint order', 'deprivation of liberty',
                      'drug offences', 'dwelling burglary', 'fraud & related offences', 'graffiti', 'homicide', 'non-dwelling burglary',
                      'property damage', 'robbery', 'sexual offences', 'stealing', 'stealing of motor vehicle', 'threatening behaviour (family)',
                      'threatening behaviour (non-family)']

        self.year = ['2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21']

        self.month =  ['jul','aug','sep','oct','nov','dec','jan','feb','mar','apr','may','jun']

        self.quarter = ['jul-sep','oct-dec','jan-mar','apr-jun']

        # initalises combo boxes
        self.Station_comboxBox.addItems(self.station)
        self.District_comboBox_2.addItems(self.district)
        self.Region_comboBox_3.addItems(self.region)
        self.Year_comboBox_6.addItems(self.year)
        self.Monthly_comboBox_5.addItems(self.month)
        self.Quarterly_comboBox_4.addItems(self.quarter)
        self.Type_comboBox_7.addItems(self.crime)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())