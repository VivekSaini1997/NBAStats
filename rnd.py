from pyqtgraph.widgets.PlotWidget import PlotWidget
import pyqtgraph as pg
import pyqtgraph.Qt as Qt

class Graph(PlotWidget):
  def __init__(self, parent=None):
    PlotWidget.__init__(self, parent)
    self._viewBoxes = [self.plotItem.getViewBox()]
    self._viewBoxes[0].register("axis 0")
    for i in range(2):
      vb = pg.ViewBox(name="axis %s" %(i+1))
      self.plotItem.scene().addItem(vb)
      vb.setXLink(self.plotItem)
      self._viewBoxes.append(vb)
    self._axes = [pg.AxisItem('left') for _ in range(3)]
    for c in zip(self._viewBoxes, self._axes):
      vb, ax = c
      ax.linkToView(vb)

    self._curves = [self.plotItem.plot()]
    for vb in self._viewBoxes[1:]:
      plotDataItem = pg.PlotDataItem()
      vb.addItem(plotDataItem)
      self._curves.append(plotDataItem)

    for p in self._viewBoxes[1:]:
      p.setGeometry(self.plotItem.vb.sceneBoundingRect())
      p.linkedViewChanged(self.plotItem.vb, p.XAxis)

    self._curves[0].setData(x=[1,2,3,4],y=[0,4,0,4], pen="b")
    self._curves[1].setData(x=[1,2,3,4],y=[0,1,2,1], pen="y")
    self._curves[2].setData(x=[1,2,3,4],y=[0,-8,8,7], pen="r")

app = Qt.QtGui.QApplication([])
graph1 = Graph()
graph1.show()
app.exec_()