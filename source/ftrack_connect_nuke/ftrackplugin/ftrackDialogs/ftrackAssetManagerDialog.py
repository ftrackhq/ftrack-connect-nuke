from ftrack_connect_nuke.ftrackplugin import ftrackConnector
from PySide import QtGui

from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.AssetManagerWidget import AssetManagerWidget
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import HeaderWidget


class ftrackAssetManagerQt(QtGui.QDialog):
    def __init__(self, parent=None):
        if not parent:
            self.parent = ftrackConnector.Connector.getMainWindow()

        super(ftrackAssetManagerQt, self).__init__(self.parent)
        self.setMinimumWidth(400)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.verticalMainLayout.setSpacing(6)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.headerWidget = HeaderWidget(self)
        self.headerWidget.setTitle('Asset Manager')
        self.verticalMainLayout.addWidget(self.headerWidget)

        self.assetManagerWidget = AssetManagerWidget(self.centralwidget)

        self.horizontalLayout.addWidget(self.assetManagerWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackAssetManager')
        self.setWindowTitle("ftrackAssetManager")

        panelComInstance = ftrackConnector.panelcom.PanelComInstance.instance()
        panelComInstance.addRefreshListener(self.assetManagerWidget.refreshAssetManager)


class ftrackAssetManagerDialog(ftrackConnector.Dialog):
    def __init__(self):
        super(ftrackAssetManagerDialog, self).__init__()
        self.dockName = 'ftrackAssetManager'
        self.panelWidth = 650

    def initGui(self):
        return ftrackAssetManagerQt

    @staticmethod
    def accepts():
        return []

    @staticmethod
    def category():
        return 'assetmanager'
