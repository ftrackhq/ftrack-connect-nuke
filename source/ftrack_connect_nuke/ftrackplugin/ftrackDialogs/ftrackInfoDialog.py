from ftrack_connect_nuke.ftrackplugin import ftrackConnector
import os
import ftrack
from PySide import QtGui

from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.WebViewWidget import WebViewWidget
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import HeaderWidget


class ftrackInfoQt(QtGui.QDialog):
    def __init__(self, parent=None):
        if not parent:
            self.parent = ftrackConnector.Connector.getMainWindow()
        super(ftrackInfoQt, self).__init__(self.parent)
        self.setMinimumWidth(400)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()

        if 'FTRACK_TASKID' in os.environ:
            taskId = os.environ['FTRACK_TASKID']
        else:
            taskId = os.environ['FTRACK_SHOTID']

        self.headerWidget = HeaderWidget(self)

        self.verticalMainLayout.addWidget(self.headerWidget)

        self.infoWidget = WebViewWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.infoWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackInfo')
        self.setWindowTitle("ftrackInfo")

        self.homeTaskId = taskId

        self.setObject(taskId)

        panelComInstance = ftrackConnector.panelcom.PanelComInstance.instance()
        panelComInstance.addInfoListener(self.updateObj)

    def setObject(self, taskId):
        obj = ftrackConnector.Connector.objectById(taskId)
        self.headerWidget.setTitle('Info panel')  # (' + obj.getParent().getName() + ' / ' + obj.getName() + ')')
        url = obj.getWebWidgetUrl('info', theme='tf')
        self.infoWidget.setUrl(url)

    def updateObj(self, taskId):
        self.setObject(taskId)


class ftrackInfoDialog(ftrackConnector.Dialog):
    def __init__(self):
        super(ftrackInfoDialog, self).__init__()
        self.dockName = 'ftrackInfo'
        self.panelWidth = 500

    def initGui(self):
        return ftrackInfoQt

    @staticmethod
    def category():
        return 'info'

    @staticmethod
    def accepts():
        return ['maya']