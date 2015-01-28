from ftrack_connect_nuke.ftrackplugin import ftrackConnector
from PySide import QtGui

from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.WebViewWidget import WebViewWidget
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import HeaderWidget

import ftrack


class ftrackTasksQt(QtGui.QDialog):
    def __init__(self, parent=None):
        if not parent:
            self.parent = ftrackConnector.Connector.getMainWindow()
        super(ftrackTasksQt, self).__init__(self.parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.setMinimumWidth(500)
        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.headerWidget = HeaderWidget(self)
        self.headerWidget.setTitle('Tasks')
        self.verticalMainLayout.addWidget(self.headerWidget)

        self.tasksWidget = WebViewWidget(self)
        
        url = ftrack.getWebWidgetUrl('tasks', theme='tf')
        
        self.tasksWidget.setUrl(url)
        self.horizontalLayout.addWidget(self.tasksWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackTasks')
        self.setWindowTitle("ftrackTasks")


class ftrackTasksDialog(ftrackConnector.Dialog):
    def __init__(self):
        super(ftrackTasksDialog, self).__init__()
        self.dockName = 'ftrackTasks'
        self.panelWidth = 500

    def initGui(self):
        return ftrackTasksQt

    @staticmethod
    def category():
        return 'info'
    
    @staticmethod
    def accepts():
        return ['maya']
