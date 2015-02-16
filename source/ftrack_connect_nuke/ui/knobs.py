import os
import ftrack
import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui, QtCore
from FnAssetAPI import specifications

import ftrack_connect_nuke
from ftrack_connect_nuke.ftrackConnector.maincon import HelpFunctions
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets import HeaderWidget
from FnAssetAPI.ui.dialogs import TabbedBrowserDialog
from ftrack_connect_nuke import ftrackConnector


class TableKnob():
    def makeUI(self):
        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['', 'Filename', 'Component', 'NodeName', '', '', ''])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 25)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setColumnWidth(4, 25)
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(5, True)
        self.tableWidget.setColumnHidden(6, True)
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.tableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideLeft)
        self.tableWidget.setMinimumHeight(200)

        self.tableWidget.updateValue = self.updateValue

        return self.tableWidget

    def updateValue(self):
        pass


class FtrackPublishLocale(specifications.LocaleSpecification):
    _type = "ftrack.publish"


class BrowseKnob():
    def makeUI(self):
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setContentsMargins(0, 0, 0, 0)
        self.hlayout = QtGui.QHBoxLayout()
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget.setLayout(self.hlayout)
        
        task = ftrack.Task(os.environ['FTRACK_TASKID'])
        self._lineEdit = QtGui.QLineEdit()
        self._lineEdit.setText(HelpFunctions.getPath(task, slash=True))
        self.hlayout.addWidget(self._lineEdit)
    
        self._browse = QtGui.QPushButton("Browse")
        self.hlayout.addWidget(self._browse)
        
        QtCore.QObject.connect(self._browse, QtCore.SIGNAL('clicked()'), self.openBrowser)
        
        self.targetTask = task.getEntityRef()
                
        return self.mainWidget
    
    def updateValue(self):
        pass
    
    def openBrowser(self):
        session = FnAssetAPI.SessionManager.currentSession()
        context = session.createContext()
        context.access = context.kWrite
        context.locale = FtrackPublishLocale()
        spec = specifications.ImageSpecification()
        spec.referenceHint = ftrack.Task(os.environ['FTRACK_TASKID']).getEntityRef()
        browser = TabbedBrowserDialog.buildForSession(spec, context)
        browser.setWindowTitle(FnAssetAPI.l("Publish to"))
        browser.setAcceptButtonTitle("Set")
        if not browser.exec_():
            return ''
        
        self.targetTask = browser.getSelection()[0]
        obj = ftrackConnector.Connector.objectById(self.targetTask)
        self._lineEdit.setText(HelpFunctions.getPath(obj, slash=True))
        

class HeaderKnob():
    def makeUI(self):
        self.headerWidget = HeaderWidget.HeaderWidget(parent=None)
        self.headerWidget.setTitle('Publish')

        self.headerWidget.updateValue = self.updateValue

        return self.headerWidget

    def updateValue(self):
        pass
