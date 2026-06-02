#!/usr/bin/env python
# Using UTF8 encoding
# -*- coding: utf-8 -*-
# encoding=utf8

# System
import os
import sys
import numpy as np
#import warnings
# To avoid excessive warning messages
# warnings.filterwarnings('ignore')


os.environ["QT_API"] = "PyQt6"
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt


from fancyroman.graphics import ImageCanvas, ZoomCanvas, NavigationToolbar
from fancyroman.io import WFIimage
from fancyroman.dialogs import QFlagList

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
        
        # Toolbar
        self.createToolbar()
        
        # Initialize quality flags
        self.initializeFlags()
        
        # Status bar
        self.sb = QtWidgets.QStatusBar()
        self.sb_label = QtWidgets.QLabel("  Welcome to Fancy Roman !\n\n"+
                                         "  Click on the folder icon to open a file.")
        self.sb.addWidget(self.sb_label,1);
        #self.sb.addPermanentWidget(self.sb_label)
        #self.sb.showMessage('', 100000)
        #self.sb_label.setText(f"New text")

        # Set the layout
        self.setLayout()

        # Show
        self.show()
        
    def setLayout(self):
        # Create main widget
        self.main_widget = QtWidgets.QWidget(self)
        
        # Define canvases
        self.ic = ImageCanvas(self.main_widget, width=5, height=5, dpi=100)
        self.ic.toolbar = NavigationToolbar(self.ic, self)
        self.ic.toolbar.pan('on')
        self.zc = ZoomCanvas(self.main_widget, width=2, height=2, dpi=100)

        mainLayout = QtWidgets.QHBoxLayout(self.main_widget)
        imageWidget = QtWidgets.QWidget()
        self.imageLayout = QtWidgets.QVBoxLayout(imageWidget)
        zoomWidget = QtWidgets.QWidget()
        self.zoomLayout = QtWidgets.QVBoxLayout(zoomWidget)
                
        
        self.imageLayout.addWidget(self.ic)
        self.imageLayout.addWidget(self.ic.toolbar)
        self.zoomLayout.addWidget(self.zc)
        self.zoomLayout.addWidget(self.tb)
        self.zoomLayout.addWidget(self.sb)
        
        
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
        file.addAction(QtGui.QAction("Open ASDF",self,shortcut='',triggered=self.newFile))
        file.addAction(QtGui.QAction("Save ASDF",self,shortcut='',triggered=self.saveFile))
        # File section       
        actions = bar.addMenu('&Actions')
        actions.addAction(QtGui.QAction("Inpaint",self,shortcut='Ctrl+I',triggered=self.inpaint))
        actions.addAction(QtGui.QAction("Select mask",self,shortcut='Ctrl+M',triggered=self.selectMask))
        actions.addAction(QtGui.QAction("Fill holes",self,shortcut='Ctrl+F',triggered=self.fillholes))
        # Help section
        help = bar.addMenu('&Help')
        help.addAction(QtGui.QAction('About', self, shortcut='Ctrl+h',triggered=self.about))
        
        
    def createAction(self,iconfile,text,shortcut,action):
        icon = os.path.join(self.path0,'icons', iconfile)
        act = QtGui.QAction(QtGui.QIcon(icon), text, self)
        act.setShortcut(shortcut)
        act.triggered.connect(action)
        return act

    def createToolbar(self):
        """ Create toolbar with icons """
        
        self.tb = QtWidgets.QToolBar()
        self.tb.setObjectName('toolbar')
        self.tb.setOrientation(Qt.Orientation.Vertical)
        # Actions
        self.aboutAction = self.createAction('help.png','About','Ctrl+h',self.about)
        self.quitAction = self.createAction('exit.png', 'Quit program', 'Ctrl+q',self.fileQuit)
        self.startAction = self.createAction('open.png', 'Load new observation', 'Ctrl+n',self.newFile)
        self.saveAction = self.createAction('save.png', 'Save file', 'Ctrl+s', self.saveFile)
        self.inpaintAction = self.createAction('inpainting.png', 'Inpaint', 'Ctrl+I',self.inpaint)
        self.fillholesAction = self.createAction('hole.png', 'Fill holes', 'Ctrl+F',self.fillholes)
        self.tb.addAction(self.startAction)
        self.tb.addAction(self.quitAction)
        self.tb.addAction(self.saveAction)
        self.tb.addAction(self.aboutAction)
        self.tb.addAction(self.inpaintAction)
        self.tb.addAction(self.fillholesAction)        
       

        
    def fileQuit(self):
        """Exit the program"""
        self.close()
        
    def newFile(self):
        """Display a new image."""
        
        fd = QtWidgets.QFileDialog(self)
        fd.setDirectory(r'.')
        fd.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        fd.setNameFilter("Calibrated images (*_cal.asdf)")
        fd.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
        
        if (fd.exec()):
            fileName= fd.selectedFiles()
            print('Reading file ', fileName[0])
            # Save the file path for future reference
            self.pathFile, file = os.path.split(fileName[0])
            print('selected file is: ', fileName[0])
            self.loadFile(fileName[0])
            try:
                pass
                self.initializeImages()
            except:
                print('Failed to initialize images')
                
    def saveFile(self):
        """ save file in new file """
        # Dialog to save file
        fd = QtWidgets.QFileDialog(self)
        fd.setWindowTitle("Save File")
        suggestedName = self.WFI.filename[:-8]+'copy_cal.asdf'
        fd.selectFile(suggestedName)
        fd.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        fd.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)

        if fd.exec():
            outfile = fd.selectedFiles()[0]
            self.WFI.save(name=outfile)
            
            
    def loadFile(self, infile):
        # Read the spectral cube
        try:
            self.WFI = WFIimage(infile)
        except:
            print("Failed to read the image")
            
    def initializeImages(self):
        """Initialize images in canvases"""
        
        image = self.WFI.image
        wcs = self.WFI.wcs
        dq = self.WFI.dq
        print('initializing image ...')
        self.ic.compute_initial_figure(image=image, wcs=wcs, dq=dq)
        self.zdelta = 50
        self.x1, self.x2 = 2000 - self.zdelta, 2000 + self.zdelta
        self.y1, self.y2 = 2000 - self.zdelta, 2000 + self.zdelta
        self.zc.compute_initial_figure(image=image[self.y1:self.y2, self.x1:self.x2], norm=self.ic.norm)
        # Connect movement of mouse to update of the zoom
        self.ic.mpl_connect('motion_notify_event', self.updateZoom)

    def initializeFlags(self):
        """ Define quality flags"""
        from roman_datamodels.dqflags import pixel
    
        self.flagnames = []
        self.flagstates = []
        self.flagvalues = []
        for p in pixel:
            self.flagnames.append(p.name)
            self.flagvalues.append(p.value)
            if p.name == 'SATURATED':
                self.flagstates.append(True)
            else:
                self.flagstates.append(False)

        
    def about(self):
        #from fifimon import __version__
        # Get path of the package
        #path0,file0 = os.path.split(__file__)
        #file=open(os.path.join(path0,"copyright.txt"),"r")
        #message=file.read()
        message = 'Fancy Roman is a code to make your Roman images fancier'
        QtWidgets.QMessageBox.about(self, "About", message)
        
    def updateZoom(self, event):
        """ Update spectrum when moving an aperture on the image """
        # Update bias and contrast with third mouse button
        if event.inaxes:
            x, y = int(event.xdata), int(event.ydata)
            if x - self.zdelta < 0:
                self.x1 = 0
                self.x2 = self.zdelta * 2 + 1
            else:
                self.x1 = x - self.zdelta
                self.x2 = x + self.zdelta
            if x + self.zdelta >= 4088:
                self.x2 = 4087
                self.x1 = 4087 - 2 * self.zdelta - 1
            if y - self.zdelta < 0:
                self.y1 = 0
                self.y2 = self.zdelta * 2 + 1
            else:
                self.y1 = y - self.zdelta
                self.y2 = y + self.zdelta
            if y + self.zdelta >= 4087:
                self.y2 = 4087
                self.y1 = 4087 - 2 * self.zdelta - 1
            self.zc.updateImage(self.WFI.image[self.y1:self.y2, self.x1:self.x2])
            
            
            
    def inpaint(self):
        """ inpaint NaN pixels """
        try:
            from maskfill import maskfill
            #idx = ~np.isfinite(self.WFI.image)
            mask = np.zeros(np.shape(self.WFI.dq), dtype=np.bool)
            for state, value in zip(self.flagstates, self.flagvalues):
                if state == True:
                    mask |= (self.WFI.dq & value) == value
            
            if np.sum(mask) > 0:
                self.WFI.image,_ = maskfill(self.WFI.image, mask, operator='median' , size=3, smooth=True)
                # Redraw the images
                self.ic.updateImage(self.WFI.image)
                self.zc.updateImage(self.WFI.image[self.y1:self.y2, self.x1:self.x2])
        except:
            print('No image to inpaint')
            
            
    def selectMask(self):
        """ select pixels to inpaint """
        selectQF = QFlagList(self.flagnames, self.flagstates)
        if selectQF.exec() == True:
            self.flagstates = selectQF.save()
        else:
            print("Canceled")
        

    def fillholes(self):
        """ eliminate low value pixels  """
        try:
            med = np.nanmedian(self.WFI.image)
            res = self.WFI.image - med
            mad = np.nanmedian(np.abs(res)) * 1.4826 # in the case of Gaussian distribution
            idx = (self.WFI.image < 0) | (res < -3*mad)
            if np.sum(idx) > 0:
                # Add median with noise of image
                n = np.sum(idx)
                self.WFI.image[idx] = med + np.random.rand(n) * mad
                # Redraw the images
                self.ic.updateImage(self.WFI.image)
                self.zc.updateImage(self.WFI.image[self.y1:self.y2, self.x1:self.x2])
        except:
            print('No image to fill')

def main():
    from fancyroman import __version__
    print('FancyRoman version ', __version__)
    
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationVersion(__version__)
    screen_resolution = app.primaryScreen().geometry()
    #width = screen_resolution.width()
    height = screen_resolution.height()
    aw = MainWindow()
    #aw.setGeometry(100, 100, int(width*0.5), int(width*0.4))
    #aw.hsplitter.setSizes ([int(width*0.4),int(width*0.1)])
    aw.setGeometry(100, 100, int(height*1.2), int(height*0.9))
    aw.hsplitter.setSizes ([int(height*0.9),int(height*0.3)])
    progname = 'Fancy Roman'
    aw.setWindowTitle("%s" % progname)
    sys.exit(app.exec())
