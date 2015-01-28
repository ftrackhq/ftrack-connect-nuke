# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FilePublish.ui'
#
# Created: Wed Jul 10 10:38:19 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FilePublish(object):
    def setupUi(self, FilePublish):
        FilePublish.setObjectName("FilePublish")
        FilePublish.resize(825, 524)
        self.verticalLayout = QtGui.QVBoxLayout(FilePublish)
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerWidget = HeaderWidget(FilePublish)
        self.headerWidget.setObjectName("headerWidget")
        self.verticalLayout.addWidget(self.headerWidget)
        self.filePublishTable = QtGui.QTableWidget(FilePublish)
        self.filePublishTable.setObjectName("filePublishTable")
        self.filePublishTable.setColumnCount(0)
        self.filePublishTable.setRowCount(0)
        self.verticalLayout.addWidget(self.filePublishTable)
        self.progressBar = QtGui.QProgressBar(FilePublish)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(FilePublish)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 0))
        self.cancelButton.setMaximumSize(QtCore.QSize(100, 30))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.okButton = QtGui.QPushButton(FilePublish)
        self.okButton.setMaximumSize(QtCore.QSize(100, 30))
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FilePublish)
        QtCore.QMetaObject.connectSlotsByName(FilePublish)

    def retranslateUi(self, FilePublish):
        FilePublish.setWindowTitle(QtGui.QApplication.translate("FilePublish", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("FilePublish", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("FilePublish", "OK", None, QtGui.QApplication.UnicodeUTF8))

from HeaderWidget import HeaderWidget
