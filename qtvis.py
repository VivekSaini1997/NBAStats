# visualization using Qt5 instead

import numpy as np
import scraper
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, \
    QLabel, QMenuBar, QMenu, QAction, QGridLayout, QSpacerItem, QComboBox, QHBoxLayout, \
    QFrame
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtGui import QPainter, QPixmap, QColor
# import PyQt5.QtWidgets
import pyqtgraph as pg
import scraper
import json
import os

# a class to encompass the tooltip displayed on hover of an element
# sublclasses QLabel to make life as easy as possible
# also takes in the a dict of team logos for faster computation
class Tooltip(QLabel):
    def __init__(self, widget, logos, *args, **kwargs):
        super().__init__(widget, *args, **kwargs)
        # init the pixmap, painter, and label
        self.logos = logos
        self.pixmap = None
        self.painter = None
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
    
    # update the tooltip based on the player's data
    # including the name of the player and their stats
    # also pass in the names of the stats to be displayed and the cursor pos
    def update(self, data, statnames):
        player = data['player']
        stats = data['stats']
        # load the right team logo
        self.pixmap = self.logos[stats['TEAM']].copy()
        self.painter = QPainter(self.pixmap)

        # draw a translucent black overlay to darken the image
        self.painter.drawRect(0, 0, 150, 100)
        self.painter.fillRect(0, 0, 150, 100, QColor(0, 0, 0, 220))
        # write some text in white
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.drawText(5, 20, '{}'.format(player))
        stat1, stat2 = statnames
        self.painter.drawText(5, 20 + 20, '{}: {}'.format(stat1, stats[stat1]))
        self.painter.drawText(5, 20 + 36, '{}: {}'.format(stat2, stats[stat2]))
        self.painter.end()
        # set the tooltip to be visible
        self.setPixmap(self.pixmap)
        self.setVisible(True)

    def enterEvent(self, event):
        self.setVisible(False)


# my window subclasses QMainWindow
# needs to in order to access the methods associated with the main window
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.allstats = scraper.load_agg_jsons(range(1996, 2020), 'fixed_json')
        self.readSettingsFile()
        self.selectSeason()
        self.loadLogos()
        self.loadStatHelp()
        self.initGUI()

    # load a specified year's dataset from the default dict
    def selectSeason(self):
        season = self.defaultvals['season']
        self.stats = self.allstats[season]

    # read in a settings file and use that to determine the starting stats 
    def readSettingsFile(self, filepath='settings.json'):
        if os.path.isfile(filepath):
            with open(filepath) as settingsfile:
                self.defaultvals = json.load(settingsfile)
        else: 
            self.defaultvals = {'season': '2019-2020', 'xstat': 'PTS', 'ystat': 'AST'}

    # write the current settings to the file 
    def writeSettingsFile(self, filepath='settings.json'):
        with open(filepath, 'w+') as settingsfile:
            json.dump(self.defaultvals, settingsfile)

    def initGUI(self):
        # set the window geometry 
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowTitle("NBA Stats")
        self.setStyleSheet("QMainWindow { background-color: #181818; } QLabel{ color: #c0c0c0; }")


        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)

        # init everything then draw
        self.initComboBoxes()
        self.initScatterPlot()
        self.initLabels()
        self.initStatHelpButtons()
        self.drawPoints()
        self.manageLayout()
        self.initMenuBar()

    def initScatterPlot(self):
        self.scatterwidget = pg.GraphicsLayoutWidget()
        self.scatterplot = self.scatterwidget.addPlot()
        self.scatterplotitem = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
        self.scatterplot.addItem(self.scatterplotitem)
        self.lastpointedat = None

        # Tooltip stuff
        self.scattertooltip = Tooltip(self.scatterwidget, self.teampixmaps)

        self.scatterplotitem.scene().sigMouseMoved.connect(self.onHover)

    def initStatComboBoxes(self):
        # create two comboboxes
        # one on the left and one on the bottom
        self.lcombobox = QComboBox(self)
        self.bcombobox = QComboBox(self)
        self.bcombobox.setFixedWidth(80)
        self.lcombobox.setFixedWidth(80)
        
        # this is a fancy way of extracting the names of the stats
        # neccessary because of how the jsons are formatted
        for elem in list(self.stats[next(iter(self.stats))])[1:]:
            self.lcombobox.addItem(elem)
            self.bcombobox.addItem(elem)

        # use the values from the settings file to determine the 
        # starting values for the boxes
        lindex = self.lcombobox.findText(self.defaultvals['ystat'])
        bindex = self.lcombobox.findText(self.defaultvals['xstat'])

        self.lcombobox.setCurrentIndex(lindex)
        self.bcombobox.setCurrentIndex(bindex)
        # keep track of previous indicies
        self.previouslindex = self.lcombobox.currentIndex()
        self.previousbindex = self.bcombobox.currentIndex()

        self.bcombobox.currentIndexChanged.connect(self.onStatSelect)
        self.lcombobox.currentIndexChanged.connect(self.onStatSelect)

    # intialize the combo box that's used to select the year for the dataset
    def initYearComboBox(self):
        # create the combobox and populate
        self.ycombobox = QComboBox(self)
        for year in range(1996, 2020):
            self.ycombobox.addItem("{}-{}".format(year, year+1))

        self.ycombobox.setFixedWidth(80)

        # default to the latest year
        yindex = self.ycombobox.findText(self.defaultvals['season'])
        self.ycombobox.setCurrentIndex(yindex)
        self.ycombobox.currentIndexChanged.connect(self.onYearSelect)

    def initComboBoxes(self):
        self.initStatComboBoxes()
        self.initYearComboBox()

    # on year select, change the dataset, then draw the points
    def onYearSelect(self):
        self.stats = self.allstats[self.ycombobox.currentText()]
        self.drawPoints()
        # update the default vals dict for when settings are written to file
        self.defaultvals['season'] = self.ycombobox.currentText()

    # write to the settings file on close
    def closeEvent(self, event):
        self.writeSettingsFile()
        super().closeEvent(event)


    # on stat select, check that the two indicies are equal
    # if they are, do a swap
    # then draw the points for the stats 
    def onStatSelect(self):
        if self.lcombobox.currentIndex() == self.bcombobox.currentIndex():
            if self.sender() == self.lcombobox:
                self.bcombobox.setCurrentIndex(self.previouslindex)
            else:
                self.lcombobox.setCurrentIndex(self.previousbindex)
        
        self.previouslindex = self.lcombobox.currentIndex()
        self.previousbindex = self.bcombobox.currentIndex()

        self.drawPoints()
        # update the defaultvals as well 
        self.defaultvals['xstat'] = self.bcombobox.currentText()
        self.defaultvals['ystat'] = self.lcombobox.currentText()

    # load in all of the teams logos from the logos directory
    # used to save precious file I/O
    def loadLogos(self, logodir='logos/'):
        self.teampixmaps = dict()
        for filename in os.listdir(logodir):
            if filename.endswith('.gif'):
                self.teampixmaps[filename[:3]] = QPixmap(logodir + filename)

    # on hover, update the item's tooltip
    # TODO: update this
    def onHover(self, pos):
        act_pos = self.scatterplotitem.mapFromScene(pos)
        p1 = self.scatterplotitem.pointsAt(act_pos)
        if p1:
            data = p1[0].data()
            statnames = (self.lcombobox.currentText(), self.bcombobox.currentText())
            self.scattertooltip.update(data, statnames)        
            # draw the box to the mouse location
            # to the left of the cursor if near the edge of the window
            # TODO: stop hardcoding the logo width and height
            if pos.x() > self.size().width() - 260:
                self.scattertooltip.setGeometry(pos.x() - 160, pos.y(), 150, 100)
            else:
                self.scattertooltip.setGeometry(pos.x() + 10, pos.y(), 150, 100)
            if self.lastpointedat is not None:
                self.lastpointedat.setSize(10)
            p1[0].setSize(20)
            self.lastpointedat = p1[0]
        else:
            self.scattertooltip.setVisible(False)
            if self.lastpointedat is not None:
                self.lastpointedat.setSize(10)
            self.lastpointedat = None



    # draw the points depending on what categories are selected
    def drawPoints(self):
        ltext = self.lcombobox.currentText()
        btext = self.bcombobox.currentText()

        # clear items before drawing
        self.scatterplotitem.clear()
        self.spots = list()
        # not a list comprension to make exception handling a bit easier
        for player in self.stats:
            try:
                self.spots.append({
                # add a tiny bit of variance to the x and y so that they don't overlap
                'x': self.stats[player][btext] + np.random.randn()/100, 
                'y': self.stats[player][ltext] + np.random.randn()/100, 
                'brush': np.random.randint(0, 255),
                'size': 10,
                'symbol': np.random.randint(0, 5),
                'data': {'player': player, 'stats': self.stats[player]}
                })
            except:
                print(player)

        self.scatterplotitem.addPoints(self.spots)
        
        # now resize the axes as neccessary to center the graph
        self.x = np.array([ p['x'] for p in self.spots ])
        self.y = np.array([ p['y'] for p in self.spots ])

        self.scatterplot.setXRange(min(self.x) - 0.5, max(self.x) + 0.5)
        self.scatterplot.setYRange(min(self.y) - 0.5, max(self.y) + 0.5)

        # also update the stats while we're here
        self.updateStats()

    # actually add widgets to the layout
    # all the layout management is done here to make changing the layout ezpz
    def manageLayout(self):
        self.grid = QGridLayout()
        self.grid.addWidget(self.ycombobox, 0, 1, alignment=Qt.AlignCenter)
        # self.grid.addWidget(self.lcombobox, 1, 0)
        self.grid.addWidget(self.scatterwidget, 1, 1)
        # self.grid.addWidget(self.bcombobox, 2, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.statlabel, 3, 0, 1, 2)
        self.grid.addWidget(self.helplabel, 4, 0, 1, 2)

        self.lhbox = QHBoxLayout()
        # self.lhbox.addStretch(1)
        self.lhbox.addWidget(self.lcombobox)
        self.lhbox.addWidget(self.lhelpbtn)

        self.bhbox = QHBoxLayout()
        # self.bhbox.addStretch(1)
        self.bhbox.addWidget(self.bcombobox)
        self.bhbox.addWidget(self.bhelpbtn)

        self.grid.addLayout(self.lhbox, 1, 0)
        self.grid.addLayout(self.bhbox, 2, 1, alignment=Qt.AlignCenter)

        self.mainWidget.setLayout(self.grid)


    # update the statistical information for the current dataset
    def updateStats(self):
        self.meanx = np.mean(self.x)
        self.meany = np.mean(self.y)
        self.varx = np.var(self.x)
        self.vary = np.var(self.y)
        self.statlabel.setText("Mean in {0}: {2}\nMean in {1}: {3}\nVariance in {0}: {4}\nVariance in {1}: {5}\n".format(
            self.bcombobox.currentText(), self.lcombobox.currentText(), self.meanx, self.meany, self.varx, self.vary
        ))

    # initialize all of the labels
    def initLabels(self):
        self.statlabel = QLabel(self)
        self.helplabel = QLabel(self)
        self.helplabel.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.helplabel.setLineWidth(2)

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

    # initialize the glossary that stores stat descriptions
    def loadStatHelp(self, filename='Stats.json'):
        # load it in first
        with open(filename) as f:
            self.statsglossary = json.load(f)

    # initialize the qt buttons to actually get help
    def initStatHelpButtons(self):
        self.lhelpbtn = QPushButton('?', self)
        self.bhelpbtn = QPushButton('?', self)

        # call the show stat help function
        self.lhelpbtn.clicked.connect(lambda : self.showStatHelp(self.lcombobox.currentText()))
        self.bhelpbtn.clicked.connect(lambda : self.showStatHelp(self.bcombobox.currentText()))

    # given a stat, show help for it
    # for now it's gonna print
    # TODO: integrate into UI
    def showStatHelp(self, statname):
        desc = self.statsglossary[statname.lower()]
        self.helplabel.setText("Name: {}\nDefinition: {}\nType: {}".format(
            desc['Name'], desc['Definition'], desc['Type']
        ))
    

def displayWindow():
    app = QApplication([])
    app.setStyle("Fusion")
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

displayWindow()