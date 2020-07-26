# visualization using Qt5 instead

import numpy as np
import scraper
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, \
    QLabel, QMenuBar, QMenu, QAction, QGridLayout, QSpacerItem, QComboBox
from PyQt5.QtCore import QMetaObject, Qt
# import PyQt5.QtWidgets
import pyqtgraph as pg
import scraper

msgs = [
    'YOU FOOL',
    'YOU IMBECILE',
    'YOU INGRATE',
    'YOU SIMPLETON',
    'YOU NEMATODE'
]

list_ = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g'
]

# my window subclasses QMainWindow
# needs to in order to access the methods associated with the main window
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.stats = scraper.load_agg_jsons(range(2019, 2020), 'fixed_json')['2019-2020']
        self.initGUI()

    def initGUI(self):
        # set the window geometry 
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowTitle("Tech With Tim")
        self.setStyleSheet("QMainWindow { background-color: #181818; } QLabel{ color: #c0c0c0; }")


        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        # create a grid layout
        self.grid = QGridLayout()

        self.initComboBoxes()
        self.initScatterPlot()
        self.drawPoints()
        self.manageLayout()

        # self.grid.setRowMinimumHeight(1)
        self.mainWidget.setLayout(self.grid)

        self.initMenuBar()

    def initScatterPlot(self):
        self.scatterwidget = pg.GraphicsLayoutWidget()
        self.scatter = self.scatterwidget.addPlot()
        self.s2 = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
        self.scatter.addItem(self.s2)

    def initComboBoxes(self):
        # create two comboboxes
        # one on the left and one on the bottom
        self.lcombobox = QComboBox(self)
        self.bcombobox = QComboBox(self)
        
        for elem in list(self.stats[next(iter(self.stats))])[1:]:
            self.lcombobox.addItem(elem)
            self.bcombobox.addItem(elem)

        self.lcombobox.setCurrentIndex(0)
        self.bcombobox.setCurrentIndex(1)
        # keep track of previous indicies
        self.previouslindex = self.lcombobox.currentIndex()
        self.previousbindex = self.bcombobox.currentIndex()

        self.bcombobox.setFixedWidth(80)
        self.lcombobox.setFixedWidth(80)

        self.bcombobox.currentIndexChanged.connect(self.onSelect)
        self.lcombobox.currentIndexChanged.connect(self.onSelect)

    # on select, check that the two indicies are equal
    # if they are, do a swap
    def onSelect(self):
        if self.lcombobox.currentIndex() == self.bcombobox.currentIndex():
            if self.sender() == self.lcombobox:
                self.bcombobox.setCurrentIndex(self.previouslindex)
            else:
                self.lcombobox.setCurrentIndex(self.previousbindex)
        
        self.previouslindex = self.lcombobox.currentIndex()
        self.previousbindex = self.bcombobox.currentIndex()

    # draw the points depending on what categories are selected
    def drawPoints(self):
        ltext = self.lcombobox.currentText()
        btext = self.bcombobox.currentText()

        self.spots = [ {
            # add a tiny bit of variance to the x and y so that they don't overlap
            'x': self.stats[player][ltext] + np.random.randn()/100, 
            'y': self.stats[player][btext] + np.random.randn()/100, 
            'brush': np.random.randint(0, 255),
            'size': 10,
            'symbol': np.random.randint(0, 5),
            'data': {'player': player, 'stats': self.stats[player]}
            } for player in self.stats ]

        self.s2.addPoints(self.spots)
        pass

    # actually add widgets to the layout
    def manageLayout(self):
        self.grid.addWidget(self.lcombobox, 0, 0)
        self.grid.addWidget(self.scatterwidget, 0, 1)
        # self.grid.addWidget(self.b1, 1, 0)
        self.grid.addWidget(self.bcombobox, 1, 1, alignment=Qt.AlignCenter)


    def initMenuBar(self):
        # create a menubar at the top?
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(0, 0, 800, 26)
        self.menubar.setObjectName("menubar")

        # and a file menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")        
        self.menuFile.setTitle("FILE")

        self.setMenuBar(self.menubar)

        # # and a new action
        self.actionNew = QAction(self)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.setText("NEW")

        # # bind everything together
        self.menuFile.addAction(self.actionNew)
        self.menubar.addAction(self.menuFile.menuAction())
        QMetaObject.connectSlotsByName(self)
        self.actionNew.triggered.connect(lambda : self.clicked("HELLO"))

    def clicked(self, text):
        self.label.setText(str(text))

    def button_clicked(self):
        self.b1.setText(msgs[random.randrange(0, len(msgs))])

def displayWindow():
    app = QApplication([])
    app.setStyle("Fusion")
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

displayWindow()