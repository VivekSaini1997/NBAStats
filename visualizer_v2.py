'''
    It's like the visualization, but better!
'''

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