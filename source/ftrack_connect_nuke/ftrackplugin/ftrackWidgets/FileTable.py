# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FileTable.ui'
#
# Created: Mon Sep  2 18:22:59 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FileTable(object):
    def setupUi(self, FileTable):
        FileTable.setObjectName("FileTable")
        FileTable.resize(983, 610)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FileTable)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.fileTableWidget = QtGui.QTableWidget(FileTable)
        self.fileTableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.fileTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.fileTableWidget.setShowGrid(False)
        self.fileTableWidget.setGridStyle(QtCore.Qt.NoPen)
        self.fileTableWidget.setObjectName("fileTableWidget")
        self.fileTableWidget.setColumnCount(0)
        self.fileTableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.fileTableWidget)

        self.retranslateUi(FileTable)
        QtCore.QMetaObject.connectSlotsByName(FileTable)

    def retranslateUi(self, FileTable):
        FileTable.setWindowTitle(QtGui.QApplication.translate("FileTable", "Form", None, QtGui.QApplication.UnicodeUTF8))

