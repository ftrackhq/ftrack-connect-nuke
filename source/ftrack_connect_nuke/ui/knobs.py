# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import ftrack
import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui, QtCore
from FnAssetAPI import specifications

import ftrack_connect_nuke
from ftrack_connect.connector import HelpFunctions
from ftrack_connect.ui.widget import header

from FnAssetAPI.ui.dialogs import TabbedBrowserDialog
from ftrack_connect_nuke import connector
from ftrack_connect.ui.theme import applyTheme
from ftrack_connect.ui import resource

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

    def __init__(self):
        self.current_task = ftrack.Task(
            os.getenv('FTRACK_TASKID',
                os.getenv('FTRACK_SHOTID')
            )
        )

        self.targetTask = self.current_task.getEntityRef()
        session = FnAssetAPI.SessionManager.currentSession()
        self.context = session.createContext()
        self.context.access = self.context.kWrite
        self.context.locale = FtrackPublishLocale()
        self.spec = specifications.ImageSpecification()
        self.spec.referenceHint = self.targetTask

    def makeUI(self):
        self.mainWidget = QtGui.QWidget()
        applyTheme(self.mainWidget, 'integration')

        self.mainWidget.setContentsMargins(0, 0, 0, 0)
        self.hlayout = QtGui.QHBoxLayout()
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget.setLayout(self.hlayout)

        self._lineEdit = QtGui.QLineEdit()
        self._lineEdit.setText(HelpFunctions.getPath(self.current_task, slash=True))
        self.hlayout.addWidget(self._lineEdit)

        self._browse = QtGui.QPushButton("Browse")
        self.hlayout.addWidget(self._browse)

        QtCore.QObject.connect(self._browse, QtCore.SIGNAL('clicked()'), self.openBrowser)

        return self.mainWidget

    def updateValue(self):
        pass

    def openBrowser(self):
        browser = TabbedBrowserDialog.buildForSession(self.spec, self.context)
        browser.setWindowTitle(FnAssetAPI.l("Publish to"))
        browser.setAcceptButtonTitle("Set")
        if not browser.exec_():
            return ''

        self.targetTask = browser.getSelection()[0]
        obj = connector.Connector.objectById(self.targetTask)
        self._lineEdit.setText(HelpFunctions.getPath(obj, slash=True))


class HeaderKnob():
    def makeUI(self):
        self.headerWidget = header.HeaderWidget(parent=None)
        applyTheme(self.headerWidget, 'integration')

        self.headerWidget.updateValue = self.updateValue

        return self.headerWidget

    def updateValue(self):
        pass
