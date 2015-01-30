from ftrack_connect_nuke import ftrackConnector
from PySide import QtGui

from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.WebViewWidget import WebViewWidget


class ftrackFeberQt(QtGui.QDialog):
    def __init__(self, parent=ftrackConnector.Connector.getMainWindow()):
        super(ftrackFeberQt, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.centralwidget = QtGui.QWidget(self)
        self.horizontalLayout = QtGui.QHBoxLayout(self)

        self.feberWidget = WebViewWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.feberWidget)

        self.setObjectName('ftrackFeber')
        self.setWindowTitle("ftrackFeber")


class ftrackFeberDialog(ftrackConnector.Dialog):
    def __init__(self):
        super(ftrackFeberDialog, self).__init__()
        self.dockName = 'ftrackFeber'

    def initGui(self):
        return ftrackFeberQt

    @staticmethod
    def accepts():
        return ['none']

    @staticmethod
    def category():
        return 'web'
