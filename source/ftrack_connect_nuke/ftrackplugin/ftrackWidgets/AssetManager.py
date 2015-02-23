# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AssetManager.ui'
#
# Created: Mon Sep 16 13:54:21 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AssetManager(object):
    def setupUi(self, AssetManager):
        AssetManager.setObjectName("AssetManager")
        AssetManager.resize(549, 419)
        self.verticalLayout = QtGui.QVBoxLayout(AssetManager)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.AssetManagerComboBox = QtGui.QComboBox(AssetManager)
        self.AssetManagerComboBox.setMaximumSize(QtCore.QSize(120, 16777215))
        self.AssetManagerComboBox.setObjectName("AssetManagerComboBox")
        self.horizontalLayout.addWidget(self.AssetManagerComboBox)
        self.versionDownButton = QtGui.QPushButton(AssetManager)
        self.versionDownButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionDownButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionDownButton.setObjectName("versionDownButton")
        self.horizontalLayout.addWidget(self.versionDownButton)
        self.versionUpButton = QtGui.QPushButton(AssetManager)
        self.versionUpButton.setMinimumSize(QtCore.QSize(20, 0))
        self.versionUpButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.versionUpButton.setObjectName("versionUpButton")
        self.horizontalLayout.addWidget(self.versionUpButton)
        self.latestButton = QtGui.QPushButton(AssetManager)
        self.latestButton.setMinimumSize(QtCore.QSize(60, 0))
        self.latestButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.latestButton.setObjectName("latestButton")
        self.horizontalLayout.addWidget(self.latestButton)
        self.selectAllButton = QtGui.QPushButton(AssetManager)
        self.selectAllButton.setMinimumSize(QtCore.QSize(80, 0))
        self.selectAllButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.selectAllButton.setObjectName("selectAllButton")
        self.horizontalLayout.addWidget(self.selectAllButton)
        self.menuButton = QtGui.QPushButton(AssetManager)
        self.menuButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.menuButton.setObjectName("menuButton")
        self.horizontalLayout.addWidget(self.menuButton)
        self.whiteSpaceLabel = QtGui.QLabel(AssetManager)
        self.whiteSpaceLabel.setText("")
        self.whiteSpaceLabel.setObjectName("whiteSpaceLabel")
        self.horizontalLayout.addWidget(self.whiteSpaceLabel)
        self.refreshButton = QtGui.QPushButton(AssetManager)
        self.refreshButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.AssertManagerTableWidget = QtGui.QTableWidget(AssetManager)
        self.AssertManagerTableWidget.setFrameShape(QtGui.QFrame.Box)
        self.AssertManagerTableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.AssertManagerTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.AssertManagerTableWidget.setObjectName("AssertManagerTableWidget")
        self.AssertManagerTableWidget.setColumnCount(0)
        self.AssertManagerTableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.AssertManagerTableWidget)

        self.retranslateUi(AssetManager)
        QtCore.QObject.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), AssetManager.refreshAssetManager)
        QtCore.QObject.connect(self.AssetManagerComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), AssetManager.filterAssets)
        QtCore.QObject.connect(self.versionDownButton, QtCore.SIGNAL("clicked()"), AssetManager.versionDownSelected)
        QtCore.QObject.connect(self.versionUpButton, QtCore.SIGNAL("clicked()"), AssetManager.versionUpSelected)
        QtCore.QObject.connect(self.latestButton, QtCore.SIGNAL("clicked()"), AssetManager.versionLatestSelected)
        QtCore.QObject.connect(self.selectAllButton, QtCore.SIGNAL("clicked()"), AssetManager.selectAll)
        QtCore.QMetaObject.connectSlotsByName(AssetManager)

    def retranslateUi(self, AssetManager):
        AssetManager.setWindowTitle(QtGui.QApplication.translate("AssetManager", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.versionDownButton.setText(QtGui.QApplication.translate("AssetManager", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.versionUpButton.setText(QtGui.QApplication.translate("AssetManager", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.latestButton.setText(QtGui.QApplication.translate("AssetManager", "Latest", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllButton.setText(QtGui.QApplication.translate("AssetManager", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.menuButton.setText(QtGui.QApplication.translate("AssetManager", "Extra", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshButton.setText(QtGui.QApplication.translate("AssetManager", "Refresh", None, QtGui.QApplication.UnicodeUTF8))

import AssetManager_rc
