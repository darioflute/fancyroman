#!/usr/bin/env python
# Using UTF8 encoding
# -*- coding: utf-8 -*-
# encoding=utf8

# System
import os
import sys
#import numpy as np
#import warnings
# To avoid excessive warning messages
# warnings.filterwarnings('ignore')


os.environ["QT_API"] = "PyQt6"
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt


from fancyroman.graphics import ImageCanvas, ZoomCanvas, NavigationToolbar

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the path of the package
        self.path0, file0 = os.path.split(__file__)
        # Define style
        with open(os.path.join(self.path0,'stylesheet.css'),"r") as fh:
            self.setStyleSheet(fh.read())

        # Menu
        self.createMenu()

        # Set the layout
        self.setLayout()

        # Show
        self.show()
        
    def setLayout(self):
        # Create main widget
        self.main_widget = QtWidgets.QWidget(self)
        
        # Define canvases
        self.ic = ImageCanvas(self.main_widget, width=5, height=5, dpi=100)
        self.mpl_toolbar = NavigationToolbar(self.ic, self)
        self.mpl_toolbar.pan('on')
        self.zc = ZoomCanvas(self.main_widget, width=4, height=4, dpi=100)

        mainLayout = QtWidgets.QHBoxLayout(self.main_widget)
        imageWidget = QtWidgets.QWidget()
        self.imageLayout = QtWidgets.QVBoxLayout(imageWidget)
        zoomWidget = QtWidgets.QWidget()
        self.zoomLayout = QtWidgets.QVBoxLayout(zoomWidget)
        
        self.imageLayout.addWidget(self.ic)
        self.zoomLayout.addWidget(self.zc)
        self.zoomLayout.addWidget(self.mpl_toolbar)
        
        
        self.hsplitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal) 
        self.hsplitter.addWidget(imageWidget)
        self.hsplitter.addWidget(zoomWidget)
        
        mainLayout.addWidget(self.hsplitter)
        self.main_widget.setLayout(mainLayout)
 
        # Create a placeholder widget to hold our toolbar and canvas.
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        

    def createMenu(self):
        """ Menu with all actions """
        
        # Main menu
        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        # File section       
        file = bar.addMenu('&File')
        file.addAction(QtGui.QAction("Quit",self,shortcut='Ctrl+q',triggered=self.fileQuit))
        # Help section
        help = bar.addMenu('&Help')
        help.addAction(QtGui.QAction('About', self, shortcut='Ctrl+h',triggered=self.about))
        
    def fileQuit(self):
        """Exit the program"""
        self.close()
        
    def about(self):
        #from fifimon import __version__
        # Get path of the package
        #path0,file0 = os.path.split(__file__)
        #file=open(os.path.join(path0,"copyright.txt"),"r")
        #message=file.read()
        message = 'Fancy Roman is a code to make your Roman images fancier'
        QtWidgets.QMessageBox.about(self, "About", message)
        

def main():
    from fancyroman import __version__
    print('FancyRoman version ', __version__)
    
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    screen_resolution = app.primaryScreen().geometry()
    width = screen_resolution.width()
    aw = MainWindow()
    aw.setGeometry(100, 100, int(width*0.8), int(width*0.4))
    progname = 'Fancy Roman'
    aw.setWindowTitle("%s" % progname)
    sys.exit(app.exec())
