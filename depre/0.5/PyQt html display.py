import sys
import io
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Folium in PyQt Example')
        self.window_width, self.window_heigth = 800,600
        self.setMinimumSize(self.window_width, self.window_heigth)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        webView = QWebEngineView()
        url = QtCore.QUrl.fromLocalFile("/testpins.html")
        webView.load(url)
        
        layout.addWidget(webView)

if __name__ =='__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''QWidget {font-size: 35px;}''')
    MyApp = MyApp()
    MyApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window')