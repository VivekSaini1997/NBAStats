# visualization using Qt5 instead

import numpy as np
import scraper
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, \
    QLabel, QMenuBar, QMenu, QAction, QGridLayout, QSpacerItem, QComboBox, QHBoxLayout, \
    QFrame, QAbstractItemView, QLineEdit, QSlider
from PyQt5.QtCore import QMetaObject, Qt, QEvent, QLine
from PyQt5.QtGui import QPainter, QPixmap, QColor
import pyqtgraph as pg
import scraper
import json
import os
import collections

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
        # write some text in white for the two stats being compared on the scatter plot
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.drawText(5, 20, '{}'.format(player))
        stat1, stat2 = statnames
        self.painter.drawText(5, 20 + 20, '{}: {}'.format(stat1, stats[stat1]))
        self.painter.drawText(5, 20 + 36, '{}: {}'.format(stat2, stats[stat2]))
        self.painter.end()
        # set the tooltip to be visible
        self.setPixmap(self.pixmap)
        self.setVisible(True)

    # undraw the tooltip if it's being hovered over
    # in order to make hovering over different points smoother
    def enterEvent(self, event):
        self.setVisible(False)

# circular buffer class
# used to implement history for the console
class CircularBuffer():

    # initialize a buffer of a given fixed size
    # and optionally default values to start at
    def __init__(self, size, values=None):
        self.start = 0
        if values:
            self.buf = values[:size] + [None] * (min(len(values), size) - size)
            self.end = min(size, len(values)) % size
        else:
            self.buf = [None] * size
            self.end = 0
        self.pos = self.end

    # append a value to the end of the buffer
    # overwrite the starting value if neccessary
    def append(self, val):
        self.buf[self.end] = val
        self.end = (self.end + 1) % len(self.buf) 
        # if start == end, that means we have hit the max capacity and need 
        # to overwrite the oldest value
        if self.start == self.end:
            self.start = (self.end + 1) % len(self.buf)
        # reset the position to the end of the list
        self.pos = self.end

    # go up and down the history
    # can't get the previous from the start or the next from the end
    def getPrevious(self):
        if self.pos != self.start:
            self.pos = (self.pos - 1) % len(self.buf)
        return self.buf[self.pos]

    def getNext(self):
        if self.pos != self.end:
            self.pos = (self.pos + 1) % len(self.buf)
        return self.buf[self.pos]

    # serialize the elements into a list and return
    def toList(self):
        ret = list()
        i = self.start
        while(i != self.end):
            ret.append(self.buf[i])
            i = (i + 1) % len(self.buf)
        return ret

# my window subclasses QMainWindow
# needs to in order to access the methods associated with the main window
class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.allstats = scraper.load_agg_jsons(range(1996, 2020), 'data/json/stats')
        self.readSettingsFile()
        self.readTeamColors()
        self.selectSeason()
        self.loadLogos()
        self.loadStatHelp()
        self.initGUI()

    # load a specified year's dataset from the default dict
    def selectSeason(self):
        season = self.defaultvals['season']
        self.stats = self.allstats[season]

    # read in a settings file and use that to determine the starting stats 
    def readSettingsFile(self, filepath='data/json/settings.json'):
        if os.path.isfile(filepath):
            with open(filepath) as settingsfile:
                self.defaultvals = json.load(settingsfile)
        else: 
            self.defaultvals = {'season': '2019-2020', 'xstat': 'PTS', 'ystat': 'AST', 'filter': ''}

    # read in the team colors
    # TODO: handle cases where a team color doesn't exist
    # that would involve using a default dict
    def readTeamColors(self, filepath='data/json/team_colors.json'):
        if os.path.isfile(filepath):
            with open(filepath) as colorsfile:
                colors = json.load(colorsfile)
        else:
            colors = dict()
        # convert to a default dict defaulting to dark gray interior, light gray exterior 
        self.teamcolors = collections.defaultdict(lambda : ('#444444', '#CCCCCC'), colors)

    # write the current settings to the file 
    def writeSettingsFile(self, filepath='data/json/settings.json'):
        with open(filepath, 'w+') as settingsfile:
            json.dump(self.defaultvals, settingsfile)

    # an event filter
    # maybe useful in the future but not now lmao
    def eventFilter(self, src, event):
        return False 

    def initGUI(self):
        # set the window geometry 
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowTitle("NBA Stats")
        self.setStyleSheet("QMainWindow { background-color: #181818; } QLabel{ color: #c0c0c0; }")

        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)

        # init everything then draw
        self.initGUIElements()
        self.drawPoints()
        self.manageLayout()
        self.initMenuBar()
   
    # init all of the GUI elements
    def initGUIElements(self):
        self.initComboBoxes()
        self.initScatterPlot()
        self.initLabels()
        self.initConsole()
        self.initSliders()

    def initScatterPlot(self):
        self.scatterwidget = pg.GraphicsLayoutWidget()
        self.scatterplot = self.scatterwidget.addPlot()

        # line for polynomial regression
        self.polyregline = None

        self.scatterplotitem = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
        self.scatterplot.addItem(self.scatterplotitem)
        self.lastpointedat = None

        # Tooltip stuff
        self.scattertooltip = Tooltip(self.scatterwidget, self.teampixmaps)
        self.scatterplotitem.scene().sigMouseMoved.connect(self.onHover)

    # perform polynomial regression to find a curve of best fit
    # TODO: maybe leverage numpy more for the polynomial fit
    def polynomialRegression(self, degree=1):
        # only on positive degrees
        degree = round(degree)
        if degree >= 1:
            X = np.ones((1, *np.shape(self.x)))
            # repeatedly stack the next power onto the X matrix
            for n in range(degree):
                X = np.vstack((X, X[-1] * self.x))
            X = X.T
            # now solve for the polynomial coefficients using the least squares method
            y = np.reshape(self.y, (*np.shape(self.y), 1))
            self.w = np.matmul(np.linalg.pinv(X), y)
            # and plot a curve using said coefficients
            resolution = 2000
            x = np.linspace(*self.scatterplot.viewRange()[0], resolution)
            y = np.zeros(resolution)
            for n in range(degree+1):
                y += (self.w[n] * np.power(x, n))
            # clear the existing polynomial regression line if it exists and plot it
            if self.polyregline:
                self.scatterplot.removeItem(self.polyregline)
            self.polyregline = self.scatterplot.plot(x, y, pen=pg.mkPen(pg.mkColor('#00E0E0'), width=3))

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

        # add help tooltips when hovering combobox items
        # TODO: format the tooltips better
        for i in range(self.lcombobox.count()):
            if self.lcombobox.itemText(i).lower() in self.statsglossary:
                desc = self.statsglossary[self.lcombobox.itemText(i).lower()]['Definition']
                self.lcombobox.setItemData(i, desc, Qt.ToolTipRole)
                self.bcombobox.setItemData(i, desc, Qt.ToolTipRole)
      
        # use the values from the settings file to determine the 
        # starting values for the boxes
        lindex = self.lcombobox.findText(self.defaultvals['ystat'])
        bindex = self.lcombobox.findText(self.defaultvals['xstat'])

        self.lcombobox.setCurrentIndex(lindex)
        self.bcombobox.setCurrentIndex(bindex)
        # keep track of previous indicies
        self.previouslindex = self.lcombobox.currentIndex()
        self.previousbindex = self.bcombobox.currentIndex()

        # update the scatter plot when you change stats
        self.bcombobox.currentIndexChanged.connect(self.onStatSelect)
        self.lcombobox.currentIndexChanged.connect(self.onStatSelect)

        # add tooltips for the comboboxes themselves as well
        self.updateComboBoxHelpToolTip(self.lcombobox)
        self.updateComboBoxHelpToolTip(self.bcombobox)

    # updates the help tooltip when a given combobox is hovered
    # needs to change based on what the currently selected combobox item is
    def updateComboBoxHelpToolTip(self, cb):
        if cb.currentText().lower() in self.statsglossary:
            definition = self.statsglossary[cb.currentText().lower()]['Definition']
            cb.setToolTip(definition)

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

    # initialize all of the sliders 
    # for now only needed for determining polynomial regression degree
    def initSliders(self):
        self.polyregslider = QSlider(self, orientation=Qt.Horizontal)
        self.polyregslider.setMinimum(1)
        self.polyregslider.setMaximum(10)
        self.polyregslider.setValue(2)
        self.polyregslider.setTickInterval(1)
        self.polyregslider.setGeometry(0, 0, 300, 10)
        self.polyregslider.valueChanged.connect(self.onSliderValueChanged)

    # listener for the slider
    # performs polynomial regression depending on the slider value
    def onSliderValueChanged(self):
        self.polynomialRegression(self.polyregslider.value())

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
        # and also the help tooltips
        self.updateComboBoxHelpToolTip(self.lcombobox)
        self.updateComboBoxHelpToolTip(self.bcombobox)

    # load in all of the teams logos from the logos directory
    # used to save precious file I/O
    def loadLogos(self, logodir='data/logos/'):
        self.teampixmaps = dict()
        for filename in os.listdir(logodir):
            if filename.endswith('.gif'):
                self.teampixmaps[filename[:3]] = QPixmap(logodir + filename)

    # initialize the console
    # this will be used to filter players
    def initConsole(self):
        # for now just create a lineedit somewhere
        self.console = QLineEdit()
        self.filterstring = self.defaultvals['filter']
        self.console.setText(self.filterstring)
        self.console.editingFinished.connect(self.onConsoleEditingFinish)

    # when you press enter, update the filter string and redraw the points
    # also update the filter in the settings file
    def onConsoleEditingFinish(self):
        self.filterstring = self.console.text()
        self.drawPoints()
        self.defaultvals['filter'] = self.filterstring

    # evaluate an input string and use that to generate a player filter function
    # filter will return true if player meets criteria and false otherwise
    # will return None if filter cannot be generated
    def generatePlayerFilterFunction(self, s):
        # check to see that only allowed symbols are being evaluated
        allowed = ['>', '<', '==', '<=', '>=', 'and', 'or', 'not', 'in']
        # also team names are valid as well
        teams = self.teamcolors.keys()
        w = s
        for symbol in [')', '(', ',']:
            w = w.replace(symbol, ' ')
        words = w.split()
        # keep track of encountered word so as to not double replace
        found_words = set()
        for word in words:
            # if its not an allowed symbol but rather a keyword, replace it in the original string
            # only do this once per keyword
            if word not in allowed and (word.lower() in self.statsglossary or word.lower() in ['age', 'team']):
                if word not in found_words:
                    s = s.replace(word, 'v[\'{}\']'.format(word))
                    found_words.add(word)
            # if it's a team name, make sure to enclose in quotations
            elif word not in allowed and word in teams:
                if word not in found_words:
                    s = s.replace(word, '\'{}\''.format(word))
                    found_words.add(word)
            # if it's not a float nor a keyword, return false
            elif word not in allowed:
                try:
                    float(word)
                except:
                    return None
        if not words:
            return None
        # now define the function to be returned and return it
        def playerFilter(player):
            v = self.stats[player]
            return eval(s)
        return playerFilter

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
            if pos.x() > self.scatterplot.width() - 160:
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
        # self.scatterplot.clear()
        self.scatterplotitem.clear()
        self.spots = list()
        
        # generate the player filter used to sort out players
        # also output the existing filter to the console label
        # this will be hooked into user input at some point
        # TODO: needs to be tested however
        playerFilter = self.generatePlayerFilterFunction(self.filterstring)
        self.consolelabel.setText(self.filterstring)
        if not playerFilter:
            if self.filterstring:
                self.consolelabel.setText("Unexpected word or symbol in input (make sure to have spaces around symbols)")
            def playerFilter(player): return True

        # if the player filter raises an exception, replace it with a default true function
        try:
            playerFilter(next(iter(self.stats)))
        except SyntaxError:
            self.consolelabel.setText("Syntax error while parsing input")
            self.filterstring = ''
            def playerFilter(player): return True

        # not a list comprension to make exception handling a bit easier
        for player in self.stats:
            try: 
                if playerFilter(player):
                    self.spots.append({
                    # add a tiny bit of variance to the x and y so that they don't overlap
                    'x': self.stats[player][btext] + np.random.randn()/100, 
                    'y': self.stats[player][ltext] + np.random.randn()/100, 
                    'brush': self.teamcolors[self.stats[player]['TEAM']][0],
                    'pen': self.teamcolors[self.stats[player]['TEAM']][1],
                    'size': 10,
                    'symbol': 'o',
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

        # also draw the polynomial of best fit
        self.polynomialRegression(self.polyregslider.value())
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
        self.grid.addWidget(self.statlabel, 3, 0, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.polyregslider, 3, 1, alignment=Qt.AlignRight)
        # self.grid.addWidget(self.helplabel, 4, 0, 1, 2)

        self.lhbox = QHBoxLayout()
        # self.lhbox.addStretch(1)
        self.lhbox.addWidget(self.lcombobox)
        # self.lhbox.addWidget(self.lhelpbtn)

        self.bhbox = QHBoxLayout()
        # self.bhbox.addStretch(1)
        self.bhbox.addWidget(self.bcombobox)
        # self.bhbox.addWidget(self.bhelpbtn)

        self.grid.addLayout(self.lhbox, 1, 0)
        self.grid.addLayout(self.bhbox, 2, 1, alignment=Qt.AlignCenter)

        self.grid.addWidget(self.consolelabel, 4, 0, 1, 2)
        self.grid.addWidget(self.console, 5, 0, 1, 2)


        self.mainWidget.setLayout(self.grid)


    # update the statistical information for the current dataset
    # this includes the equation for best fit
    def updateStats(self):
        self.meanx = np.mean(self.x)
        self.meany = np.mean(self.y)
        self.varx = np.var(self.x)
        self.vary = np.var(self.y)

        self.fiteq = ''
        for deg in reversed(range(len(self.w))):
            self.fiteq += '{}{}'.format(self.w[deg], ('x^{} + '.format(deg) if deg else ''))

        self.statlabel.setText(
            "Mean in {0}: {2}\nMean in {1}: {3}\nVariance in {0}: {4}\nVariance in {1}: {5}\n".format(
            self.bcombobox.currentText(), self.lcombobox.currentText(), self.meanx, self.meany, self.varx, self.vary
        ))

    # initialize all of the labels
    def initLabels(self):
        self.statlabel = QLabel(self)
        self.consolelabel = QLabel(self)

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
    def loadStatHelp(self, filename='data/json/stat_descriptions.json'):
        # load it in first
        with open(filename) as f:
            self.statsglossary = json.load(f)

def displayWindow():
    app = QApplication([])
    app.setStyle("Fusion")
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

displayWindow()