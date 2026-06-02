from PyQt6.QtWidgets import QDialog, QCheckBox

class WFIimage(object):
    """ WFI image - read with Roman Data Models routines """
    def __init__(self, infile):
        try:
            import roman_datamodels as rdm
        except ImportError:
            print('install roman_datamodels library:  pip install roman-datamodels')
            exit

        self.filename = infile
        with rdm.open(infile) as dm:
            self.image = dm.data.copy()
            self.dq = dm.dq.copy()
            self.wcs = dm.meta.wcs
            
    def save(self, name='test.asdf'):
        
        import roman_datamodels as rdm
        
        with rdm.open(self.filename) as f:
            f.data = self.image
            f.dq = self.dq
            f.save(name)
            