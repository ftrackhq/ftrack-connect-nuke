import os

from PySide import QtCore, QtGui
from FileTable import Ui_FileTable
import re


class FileTableWidget(QtGui.QWidget):
    emptyRowSignal = QtCore.Signal()
    
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FileTable()
        self.ui.setupUi(self)

        self.columnHeadersSequences = ['Path', 'Filename', 'Start', 'End', 'ComponentName', 'Del', 'Padding']
        self.ui.fileTableWidget.setColumnCount(6)
        self.ui.fileTableWidget.setHorizontalHeaderLabels(self.columnHeadersSequences)
        self.ui.fileTableWidget.horizontalHeader().setDefaultSectionSize(75)
        self.ui.fileTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.ui.fileTableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.fileTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.ui.fileTableWidget.hideColumn(6)
        self.ui.fileTableWidget.verticalHeader().hide()
        self.ui.fileTableWidget.setSortingEnabled(True)
        self.ui.fileTableWidget.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.ui.fileTableWidget.setColumnWidth(5, 40)
        self.ui.fileTableWidget.setColumnWidth(4, 200)
        self.ui.fileTableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        
        self.ui.fileTableWidget.setFrameShadow(QtGui.QFrame.Shadow.Plain)

        self.signalMapperRemove = QtCore.QSignalMapper()
        QtCore.QObject.connect(self.signalMapperRemove, QtCore.SIGNAL("mapped(QString)"), self.removeFile)

    def addFile(self, filePath, realfileName, frameStart, frameEnd):
        self.ui.fileTableWidget.setSortingEnabled(False)
        foundItems = self.ui.fileTableWidget.findItems(realfileName, QtCore.Qt.MatchStartsWith)
        if foundItems and len(foundItems) > 0:
            return

        rowcount = self.ui.fileTableWidget.rowCount()
        self.ui.fileTableWidget.insertRow(rowcount)
        pathItem = QtGui.QTableWidgetItem(filePath)
        self.ui.fileTableWidget.setItem(rowcount, 0, pathItem)

        filenameItem = QtGui.QTableWidgetItem(realfileName)
        self.ui.fileTableWidget.setItem(rowcount, 1, filenameItem)

        frameStartItem = QtGui.QTableWidgetItem(frameStart)
        self.ui.fileTableWidget.setItem(rowcount, 2, frameStartItem)

        frameEndItem = QtGui.QTableWidgetItem(frameEnd)
        self.ui.fileTableWidget.setItem(rowcount, 3, frameEndItem)

        componentName = os.path.splitext(realfileName)[0]
        componentName = re.sub('\W', '', componentName)
        componentName = re.sub('\d', '', componentName)

        componentNameItem = QtGui.QTableWidgetItem(componentName)
        self.ui.fileTableWidget.setItem(rowcount, 4, componentNameItem)

        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        widget.setLayout(layout)
        removeButton = QtGui.QPushButton('X')
        removeButton.setFixedSize(22, 22)
        
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(removeButton)
        
        self.ui.fileTableWidget.setCellWidget(rowcount, 5, widget)

        QtCore.QObject.connect(removeButton, \
                               QtCore.SIGNAL("clicked()"), \
                               self.signalMapperRemove, \
                               QtCore.SLOT("map()"))
        self.signalMapperRemove.setMapping(removeButton, realfileName)

        self.ui.fileTableWidget.setSortingEnabled(False)

    def removeFile(self, filename):
        foundItems = self.ui.fileTableWidget.findItems(filename, QtCore.Qt.MatchStartsWith)
        for item in foundItems:
            self.ui.fileTableWidget.removeRow(item.row())
            
        if self.getRowCount() == 0:
            self.emptyRowSignal.emit()
            
    def getRowCount(self):
        return self.ui.fileTableWidget.rowCount()
