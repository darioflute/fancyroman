import os

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure

from astropy import visualization
from astropy.coordinates import SkyCoord
from astropy import units as u



class NavigationToolbar(NavigationToolbar2QT):
    def __init__(self,canvas,parent):
        # Select only a few buttons
        self.iconDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons")
        self.toolitems = [
            ('Home','Go back to original limits','home','home'),
            #('Backward','Go back','back','back'),
            #('Forward','Go forward','forward','forward'),
            ('Pan','Pan figure','move','pan'),
            ('Zoom','Zoom in','zoom_to_rect','zoom'),
        ]
        self.parent = parent
        super().__init__(canvas,parent)



class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        #self.axes = fig.add_subplot(111)
        #super().__init__(self.fig)
        self.compute_initial_figure()

    def compute_initial_figure(self):
        pass


class ImageCanvas(MplCanvas):
    
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self, image=None, wcs=None, dq=None):
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
                print('No axes there')
            self.axes = self.fig.add_axes([0.1,0.1,.8,.8], projection=self.wcs)
            self.axes.coords[0].set_major_formatter('hh:mm:ss')
            self.axes.grid(color='black', ls='dashed')
            self.axes.set_xlabel('R.A.')
            self.axes.set_ylabel('Dec')
            if image is not None:
                self.dq = dq
                self.showImage(image)
            else:
                print('No image yet')
            # Activate focus
            #self.setFocusPolicy(Qt.ClickFocus)
            #self.setFocus()
            
    
    def showImage(self, image):
        # Remove pre-existing image
        try:
            self.image.remove()
        except:
            print('No image to remove')
            pass

        # showing image
        self.norm = visualization.ImageNormalize(image, interval=visualization.ZScaleInterval(contrast=1), 
                                   stretch=visualization.AsinhStretch(a=1))
        self.image = self.axes.imshow(image, norm=self.norm, origin='lower',cmap='inferno')
        # Cursor data format
         
        self.axes.format_coord = self.format_coord
        self.fig.canvas.draw_idle()
        
    def format_coord(self, x, y):
        """ Redefine how to show the coordinates """
        xx, yy = self.wcs(x,y)     
        " Transform coordinates in string "
        radec = SkyCoord(xx*u.deg, yy*u.deg, frame='icrs')
        xx = radec.ra.to_string(u.hour,sep=':',precision=2)
        yy = radec.dec.to_string(sep=':',precision=1)
        column = int(x + 0.5)
        row = int(y + 0.5)
        dqvalue = self.dq[row, column]
        format = '{:s} {:s} ({:04.0f},{:04.0f}) [{:032b}]'.format(xx,yy,x,y,dqvalue)
        return format
    
    def updateImage(self, image):
        self.image.set_data(image)
        self.fig.canvas.draw_idle()
        pass


class ZoomCanvas(MplCanvas):
    
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self, image=None, norm=None):
        if image is None:
            '''initial definition when images are not yet read'''
            self.axes = self.fig.add_axes([0.1,0.1,0.8,0.8])
            self.axes.set_axis_off()
            pass
        else:
            #self.fig.delaxes(self.axes)
            #self.axes = self.fig.add_axes([0.1,0.1,0.8,0.8])
            #self.axes.set_axis_off()
            # Show image
            self.contrast = 1.
            self.bias = 0.5
            self.showImage(image, norm=norm)
    
    def showImage(self, image, norm):
        print('Showing zoomed image')
        self.zoom = self.axes.imshow(image, norm=norm, origin='lower',cmap='inferno')
        self.fig.canvas.draw_idle()
        
    def updateImage(self, image):
        self.zoom.set_data(image)
        self.fig.canvas.draw_idle()