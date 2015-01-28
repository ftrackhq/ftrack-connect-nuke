from PySide import QtGui
from Playblast import Ui_Playblast
import ftrack
import os


class PlayblastWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Playblast()
        self.ui.setupUi(self)

        self.ui.playwithCombo.addItem('RV')

        self.ui.frameStart.setText(os.environ['FS'])
        self.ui.frameEnd.setText(os.environ['FE'])

        self.ui.stereoAna.hide()

    def getSize(self):
        if self.ui.size25.isChecked():
            return 25
        elif self.ui.size50.isChecked():
            return 50
        elif self.ui.size75.isChecked():
            return 75
        elif self.ui.size100.isChecked():
            return 100

    def getFormat(self):
        if self.ui.formatQuicktime.isChecked():
            return 'qt'
        elif self.ui.formatTiff.isChecked():
            return 'tif'

    def getStereo(self):
        if self.ui.stereoAna.isChecked():
            return 'analaglyph'
        elif self.ui.stereoMulti.isChecked():
            return 'multi'
        elif self.ui.stereoOff.isChecked():
            return 'off'

    def setRange(self, fs, fe):
        self.ui.frameStart.setText(str(fs))
        self.ui.frameEnd.setText(str(fe))

    def getRange(self):
        return int(self.ui.frameStart.text()), int(self.ui.frameEnd.text())

    def getOverscan(self):
        if self.ui.overscan.isChecked():
            return True
        else:
            return None

    def getCamera(self):
        return self.ui.cameraCombo.currentText()
    
    def getOrnaments(self):
        if self.ui.ornamentsCheck.isChecked():
            return True
        else:
            return False
    
    def updateOutputResolution(self):
        globalWidth = self.getWidth()
        globalHeight = self.getHeight()
        
        size = self.getSize()
        
        outWidth = int(float(globalWidth) * (float(size) / 100.0))
        outHeight = int(float(globalHeight) * (float(size) / 100.0))
        
        self.ui.widthFinalEdit.setText(str(outWidth))
        self.ui.heightFinalEdit.setText(str(outHeight))
        
    def getWidth(self):
        return int(self.ui.widthEdit.text())
    
    def getHeight(self):
        return int(self.ui.heightEdit.text())
