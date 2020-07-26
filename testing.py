from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np

# create the app
app = QtGui.QApplication([])
main_window = QtGui.QMainWindow()
main_window.resize(800,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
main_window.setCentralWidget(view)



# add a window to the app
viewbox = view.addViewBox()
viewbox.setAspectLocked(True)

print(type(main_window), type(viewbox))

print(dir(pg.graphicsItems.ViewBox.ViewBox))

print(type(pg.GraphItem))
main_window.show()



print('Hello World')

QtGui.QApplication.instance().exec_()


