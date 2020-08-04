import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap
import pyqtgraph as pg 
import numpy as np
import pyqtgraph.examples

pyqtgraph.examples.run()

torlogo = 'logos/TOR.gif'

im = Image.open(torlogo)
pixmap = QPixmap(torlogo)

app = QApplication(sys.argv)


x = np.arange(1000)
y = np.random.normal(size=(3, 1000))

plotWidget = pg.plot(title="lolo")

lbl = QLabel(plotWidget)

for i in range(3):
    plotWidget.plot(x, y[i], pen=(i, 3))

img = pg.ImageItem(np.array(im).T)
print(np.shape(np.array(im)))
plotWidget.addItem(img)
plotWidget.setXRange(0, 100)
plotWidget.setYRange(0, 100)
status = app.exec_()
sys.exit(status)
