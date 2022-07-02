'''
Just a seperate file for auxillary data structures
These may be phased out, but I just want to clean things up
'''

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

def UNUSED(obj):
    return

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
        UNUSED(event)
        self.setVisible(False)


# circular buffer class
# used to implement history for the console
class CircularBuffer():

    # initialize a buffer of a given fixed size
    # and optionally default values to start at
    def __init__(self, size, values=None):
        self.start = 0
        if values:
            self.buf = values[:size] + [''] * (size - min(len(values), size))
            self.end = min(size, len(values)) % size
        else:
            self.buf = [''] * size
            self.end = 0
        self.pos = self.end
        # print(self.buf)

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
        # print(self.buf)
        # print(self.toList())

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
        if self.start > self.end:
            return self.buf[self.start:] + self.buf[:self.end]
        return self.buf[self.start:self.end]