import sys
import pyqtgraph

app = pyqtgraph.QtGui.QApplication([])
win = pyqtgraph.GraphicsLayoutWidget()
qi = pyqtgraph.QtGui.QPixmap('logos/TOR.gif')
label = pyqtgraph.QtGui.QLabel(win)
label.setPixmap(qi)

win.show()


if __name__ == '__main__':
    pyqtgraph.QtGui.QApplication.instance().exec_()