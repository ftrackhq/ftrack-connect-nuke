
import traceback

from PySide import QtGui
import ftrack

from ..worker import Worker


class TransferWidget(QtGui.QWidget):
    '''Transfer components between locations.'''
    
    def __init__(self, parent=None, entity=None):
        '''Initialise widget.'''
        super(TransferWidget, self).__init__(parent)
        self._entity = None
        self.worker = None
        self.build()
        self.postBuild()

        if entity is not None:
            self.setEntity(entity)
    
    def build(self):
        '''Build widgets and layout.'''
        self.setLayout(QtGui.QVBoxLayout())
        
        # TODO: Make it possible to pick a component and in future also pick
        # versions / assets etc.
        self.entityLabel = QtGui.QLineEdit()
        self.entityLabel.setTextMargins(5, 5, 5, 5)
        self.entityLabel.setPlaceholderText('Nothing selected.')
        self.entityLabel.setEnabled(False)
        self.layout().addWidget(self.entityLabel)
        
        self.selectionLayout = QtGui.QHBoxLayout()
        self.layout().addLayout(self.selectionLayout)
        
        self.sourceSelector = QtGui.QComboBox()
        self.selectionLayout.addWidget(self.sourceSelector, stretch=1)
        
        # TODO: Replace with a nice icon
        self.transferLabel = QtGui.QLabel('->')
        self.selectionLayout.addWidget(self.transferLabel)
        
        self.targetSelector = QtGui.QComboBox()
        self.selectionLayout.addWidget(self.targetSelector, stretch=1)
        
        self.controlLayout = QtGui.QHBoxLayout()
        self.layout().addLayout(self.controlLayout)
        
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setTextVisible(False)
        self.controlLayout.addWidget(self.progressBar)
        
        self.transferButton = QtGui.QPushButton('Transfer')
        self.transferButton.setEnabled(False)
        self.controlLayout.addWidget(self.transferButton)
        
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

    def postBuild(self):
        '''Perform post build operations.'''
        self.transferButton.clicked.connect(self.transfer)
    
    def setEntity(self, entity):
        '''Set *entity* to transfer.'''
        self._entity = entity
        self.sourceSelector.clear()
        self.sourceSelector.setEnabled(True)
        self.targetSelector.clear()
        self.targetSelector.setEnabled(True)
        self.entityLabel.setText('')
        self.transferButton.setEnabled(False)
        
        if entity is None:
            return
        
        label = str(entity)
        try:
            label = entity.getName()
        except AttributeError:
            pass
        
        self.entityLabel.setText(label)
        
        locations = ftrack.getLocations()
        accessibleLocations = [location for location in locations
                               if location.getAccessor() is not None]
        
        if isinstance(entity, ftrack.Component):
            availability = entity.getAvailability(
                [location.getId() for location in accessibleLocations]
            )
            
            for location in accessibleLocations:
                locationLabel = '{0} ({1:.0f}%)'.format(
                    location.getName(),
                    availability[location.getId()]
                )
                self.targetSelector.addItem(locationLabel, location)
                
                try:
                    componentInLocation = location.getComponent(entity)
                except ftrack.FTrackError:
                    continue
                
                self.sourceSelector.addItem(locationLabel, componentInLocation)
        
        if self.sourceSelector.count() and self.targetSelector.count():
            self.transferButton.setEnabled(True)
    
    def getEntity(self):
        '''Return current entity.'''
        return self._entity
    
    def transfer(self):
        '''Perform transfer.'''
        self.transferButton.setEnabled(False)
        self.sourceSelector.setEnabled(False)
        self.targetSelector.setEnabled(False)
        
        componentInLocation = self.sourceSelector.itemData(
            self.sourceSelector.currentIndex()
        )
        targetLocation = self.targetSelector.itemData(
            self.targetSelector.currentIndex()
        )
        
        self.progressBar.setRange(0, 0)
        
        try:
            self.worker = Worker(targetLocation.addComponent,
                                 [componentInLocation],
                                 parent=self)
            self.worker.start()
    
            while self.worker.isRunning():
                app = QtGui.QApplication.instance()
                app.processEvents()
    
            if self.worker.error:
                raise self.worker.error[1], None, self.worker.error[2]
        
        except Exception as error:
            traceback.print_exc()
            QtGui.QMessageBox.critical(
                None,
                'Error',
                'An unhandled error occurred:'
                '\n{0}'.format(error)
            )
        
        finally:
            self.transferButton.setEnabled(True)
            self.sourceSelector.setEnabled(True)
            self.targetSelector.setEnabled(True)
            self.progressBar.setMaximum(1)
            self.progressBar.reset()
            self.worker = None
            self.refresh()
    
    def transferInProgress(self):
        '''Return whether a transfer is active.'''
        return self.worker is not None
    
    def refresh(self):
        '''Refresh display.'''
        self.setEntity(self.getEntity())
