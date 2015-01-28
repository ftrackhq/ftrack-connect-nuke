
from PySide import QtGui

from ftrackplugin.ftrackWidgets.transferWidget import TransferWidget


class TransferDialog(QtGui.QDialog):
    '''Manage transfers between locations.'''

    def __init__(self, parent=None, entity=None):
        '''Initialise dialog.'''
        super(TransferDialog, self).__init__(parent)
        self.build(entity)
        self.postBuild()

    def build(self, entity=None):
        '''Build widgets and layout.'''
        self.setWindowTitle('Transfer')
        self.setLayout(QtGui.QVBoxLayout())
        
        self.transferWidget = TransferWidget(entity)
        self.transferWidget.setMinimumWidth(600)
        self.layout().addWidget(self.transferWidget)
        
        self.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        
    def postBuild(self):
        '''Perform post build operations.'''

    def setEntity(self, entity):
        '''Set *entity* to transfer.'''
        self.transferWidget.setEntity(entity)
    
    def getEntity(self):
        '''Return entity.'''
        return self.transferWidget.getEntity()
    
    def reject(self):
        '''Handle rejection.'''
        if not self.transferWidget.transferInProgress():
            super(TransferDialog, self).reject()
