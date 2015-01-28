import os
from PySide import QtCore, QtGui
from Header import Ui_Header


class HeaderWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Header()
        self.ui.setupUi(self)
        #self.setMaximumHeight(40)
        self.setFixedHeight(40)
        self.helpUrl = 'http://support.ftrack.com/'

        if 'FTRACK_HEADER_LOGO' in os.environ and os.environ['FTRACK_HEADER_LOGO'] != '':
            logoPixmap = QtGui.QPixmap(os.environ['FTRACK_HEADER_LOGO'])
            self.ui.logoLabel.setPixmap(logoPixmap.scaled(self.ui.logoLabel.size(), QtCore.Qt.KeepAspectRatio))
        #else:
        #    logoPixmap = self.ui.logoLabel.pixmap()
        #    self.ui.logoLabel.setPixmap(logoPixmap)
        p = self.palette()
        currentColor = p.color(QtGui.QPalette.Window)
        p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(currentColor.darker(200)))
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def setTitle(self, title):
        self.ui.titleLabel.setText(title)
        
    def openHelp(self):
        import webbrowser
        webbrowser.open(self.helpUrl)
        
    def setHelpUrl(self, url):
        self.helpUrl = url
