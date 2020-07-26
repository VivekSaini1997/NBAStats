# -*- coding: utf-8 -*-
"""
Example demonstrating a variety of scatter plot features.
"""


from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
from collections import namedtuple
import os
import scraper
app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)
# grid = QtWidgets.QGridLayout()
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
# cbox = pg.ComboBox()
# grid.addWidget(cbox)
# grid.addWidget(view)

# create a seperate Label class to override the enter event
# used to undisplay the label when neccessary
class Label(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)

    # def enterEvent(self, ev):
    #     self.setVisible(False)

label = Label(view)
pixmap = QtGui.QPixmap('logos/TOR.gif')
painter = QtGui.QPainter(pixmap)
painter.drawRect(5, 5, 140, 90)
label.setPixmap(pixmap)
label.setVisible(False)
label.setAlignment(QtCore.Qt.AlignCenter)




## create four areas to add plots
# view.addItem(cbox)
w2 = view.addPlot()
print("Generating data, this takes a few seconds...")

mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

## There are a few different ways we can draw scatter plots; each is optimized for different types of data:

logos = ['logos/{}'.format(logo) for logo in os.listdir('logos')]
print(logos)
## 1) All spots identical and transform-invariant (top-left plot).
## In this case we can get a huge performance boost by pre-rendering the spot
## image and just drawing that image repeatedly.

n = 30


## 2) Spots are transform-invariant, but not identical (top-right plot).
## In this case, drawing is almsot as fast as 1), but there is more startup
## overhead and memory usage since each spot generates its own pre-rendered
## image.

TextSymbol = namedtuple("TextSymbol", "label symbol scale")

def createLabel(label, angle):
    symbol = QtGui.QPixmap('logos/TOR.gif')
    f = QtGui.QFont()
    f.setPointSize(10)
    return TextSymbol(label, symbol, 0.1 )

full_stats_dict = scraper.load_agg_jsons(range(1996, 2020), 'fixed_json')
season_2019_2020 = full_stats_dict['2019-2020'] 


random_str = lambda : (''.join([chr(np.random.randint(ord('A'),ord('z'))) for i in range(np.random.randint(1,5))]), np.random.randint(0, 360))

s2 = pg.PlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
# print(s2.axes)
# s2.setSymbol(label)
# s2.setLabel('left', "Y Axis", units='A')
# s2.setLabel('bottom', "Y Axis", units='s')
pos = np.random.normal(size=(2,n), scale=1e-5)
spots = [{'pos': pos[:,i], 'data': 1, 'brush':pg.intColor(i, n), 'symbol': i%5, 'size': 10.} for i in range(n)]
# apparently data can be whatever
# this is very convenient lmao
spots = [ {
    # add a tiny bit of variance to the x and y so that they don't overlap
    'x': season_2019_2020[player]['DREB'] + np.random.randn()/100, 
    'y': season_2019_2020[player]['OREB'] + np.random.randn()/100, 
    'brush': np.random.randint(0, 255),
    'size': 10,
    'symbol': np.random.randint(0, 5),
    'data': {'player': player, 'stats': season_2019_2020[player]}
    } for player in season_2019_2020 ]

# print(spots)

s2.plot(spots)

p = pg.PlotWidget()
print(s2)
p.addItem(s2)
# view.addItem(p)
# TODO: monkey patch axis items into scatter plot item

'''
['_SpotItem__plot_ref', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_data', '_index', '_plot', 'brush', 'data', 'index', 'pen', 'pos', 'resetBrush', 'resetPen', 
'setBrush', 'setData', 'setPen', 'setSize', 'setSymbol', 'size', 'symbol', 'updateItem', 'viewPos']
'''
lastPointedAt = None




def onMove(pos):
    global lastPointedAt
    act_pos = s2.mapFromScene(pos)
    p1 = s2.pointsAt(act_pos)
    if p1:
        data = p1[0].data()
        player = data['player']
        stats = data['stats']
        # print('Player: {}, OREB: {}, DREB: {}'.format(player, stats['OREB'], stats['DREB']))
        # load the right team logo
        pixmap = QtGui.QPixmap('logos/{}.gif'.format(stats['TEAM']))
        painter = QtGui.QPainter(pixmap)
        # draw a translucent black overlay to darken the image
        painter.drawRect(0, 0, 150, 100)
        painter.fillRect(0, 0, 150, 100, QtGui.QColor(0, 0, 0, 220))
        # write some text in white
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(5, 20, '{}'.format(player))
        painter.drawText(5, 20 + 20, 'OREB: {}'.format(stats['OREB']))
        painter.drawText(5, 20 + 36, 'DREB: {}'.format(stats['DREB']))

        # this gets the width in pixels of the player name and prints it
        # print(QtGui.QFontMetrics(painter.font()).horizontalAdvance(player))
        # also the height
        # print(QtGui.QFontMetrics(painter.font()).height())

        # print(mw.size())
        painter.end()
        # draw the box to the mouse location
        label.setPixmap(pixmap)
        # to the left of the cursor if near the edge of the window
        # TODO: stop hardcoding the logo width and height
        if pos.x() > mw.size().width() - 150:
            label.setGeometry(pos.x() - 160, pos.y(), 150, 100)
        else:
            label.setGeometry(pos.x() + 10, pos.y(), 150, 100)
        label.setVisible(True)
        if lastPointedAt is not None:
            lastPointedAt.setSize(10)
        p1[0].setSize(20)
        lastPointedAt = p1[0]
    else:
        label.setVisible(False)
        if lastPointedAt is not None:
            lastPointedAt.setSize(10)
        lastPointedAt = None

w2.addItem(s2)



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        s2.scene().sigMouseMoved.connect(onMove)
        QtGui.QApplication.instance().exec_()

