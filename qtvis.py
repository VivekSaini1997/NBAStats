# visualization using Qt5 instead

import numpy as np
import scraper
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, \
    QLabel, QMenuBar, QMenu, QAction, QGridLayout, QSpacerItem, QComboBox
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtGui import QPainter, QPixmap, QColor
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
        self.scatterplot = self.scatterwidget.addPlot()
        self.scatterplotitem = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
        self.scatterplot.addItem(self.scatterplotitem)
        self.lastpointedat = None

        # Tooltip stuff
        # TODO: maybe make a seperate class?
        self.scatterlabel = QLabel(self.scatterwidget)
        self.scatterpixmap = QPixmap('logos/TOR.gif')
        self.scatterpainter = QPainter(self.scatterpixmap)
        self.scatterpainter.drawRect(5, 5, 140, 90)
        self.scatterlabel.setPixmap(self.scatterpixmap)
        self.scatterlabel.setVisible(False)
        self.scatterlabel.setAlignment(Qt.AlignCenter)
        self.scatterpainter.end()

        self.scatterplotitem.scene().sigMouseMoved.connect(self.onHover)

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

        self.drawPoints()

    # on hover, update the item's tooltip
    # TODO: update this
    def onHover(self, pos):
        act_pos = self.scatterplotitem.mapFromScene(pos)
        p1 = self.scatterplotitem.pointsAt(act_pos)
        if p1:
            data = p1[0].data()
            player = data['player']
            stats = data['stats']
            # load the right team logo
            self.scatterpixmap = QPixmap('logos/{}.gif'.format(stats['TEAM']))
            self.scatterpainter = QPainter(self.scatterpixmap)

            # draw a translucent black overlay to darken the image
            self.scatterpainter.drawRect(0, 0, 150, 100)
            self.scatterpainter.fillRect(0, 0, 150, 100, QColor(0, 0, 0, 220))
            # write some text in white
            self.scatterpainter.setPen(QColor(255, 255, 255))
            self.scatterpainter.drawText(5, 20, '{}'.format(player))
            stat1 = self.lcombobox.currentText()
            stat2 = self.bcombobox.currentText()
            self.scatterpainter.drawText(5, 20 + 20, '{}: {}'.format(stat1, stats[stat1]))
            self.scatterpainter.drawText(5, 20 + 36, '{}: {}'.format(stat2, stats[stat2]))
            self.scatterpainter.end()
            # draw the box to the mouse location
            self.scatterlabel.setPixmap(self.scatterpixmap)
            # to the left of the cursor if near the edge of the window
            # TODO: stop hardcoding the logo width and height
            if pos.x() > self.size().width() - 260:
                self.scatterlabel.setGeometry(pos.x() - 160, pos.y(), 150, 100)
            else:
                self.scatterlabel.setGeometry(pos.x() + 10, pos.y(), 150, 100)
            self.scatterlabel.setVisible(True)
            if self.lastpointedat is not None:
                self.lastpointedat.setSize(10)
            p1[0].setSize(20)
            self.lastpointedat = p1[0]
        else:
            self.scatterlabel.setVisible(False)
            if self.lastpointedat is not None:
                self.lastpointedat.setSize(10)
            self.lastpointedat = None

    # draw the points depending on what categories are selected
    def drawPoints(self):
        ltext = self.lcombobox.currentText()
        btext = self.bcombobox.currentText()

        # clear items before drawing
        self.scatterplotitem.clear()
        self.spots = [ {
            # add a tiny bit of variance to the x and y so that they don't overlap
            'x': self.stats[player][btext] + np.random.randn()/100, 
            'y': self.stats[player][ltext] + np.random.randn()/100, 
            'brush': np.random.randint(0, 255),
            'size': 10,
            'symbol': np.random.randint(0, 5),
            'data': {'player': player, 'stats': self.stats[player]}
            } for player in self.stats ]

        self.scatterplotitem.addPoints(self.spots)
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