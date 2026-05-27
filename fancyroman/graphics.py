import os
from PyQt6.QtCore import Qt

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.compute_initial_figure()

    def compute_initial_figure(self):
        pass


class ImageCanvas(MplCanvas):
    
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self, image=None, wcs=None):
        if wcs is None:
            '''initial definition when images are not yet read'''
            pass
        else:
            self.wcs = wcs
            try:
                self.fig.delaxes(self.axes)
                self.axes = None
                print("Deleting axes")
            except:
                pass
            self.axes = self.fig.add_axes([0.1,0.1,.8,.8], projection = self.wcs)
            self.axes.coords[0].set_major_formatter('hh:mm:ss')
            self.axes.grid(color='black', ls='dashed')
            self.axes.set_xlabel('R.A.')
            self.axes.set_ylabel('Dec')
            # Colorbar
            self.cbaxes = self.fig.add_axes([0.9,0.1,0.02,0.85])
            # Show image
            self.contrast = 1.
            self.bias = 0.5
            if image is not None:
                self.showImage(image)
            # Activate focus
            self.setFocusPolicy(Qt.ClickFocus)
            self.setFocus()
    
    def showImage(self, image):
        print('Showing image')
        

class ZoomCanvas(MplCanvas):
    
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self, image=None):
        if image is None:
            '''initial definition when images are not yet read'''
            pass
        else:
            self.fig.delaxes(self.axes)
            self.axes = self.fig.add_axes([0.1,0.1,.8,.8], projection = self.wcs)
            # Show image
            self.contrast = 1.
            self.bias = 0.5
            self.showImage(image)
    
    def showImage(self, image):
        print('Showing image')

