# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportComponent.ui'
#
# Created: Fri Apr 12 13:51:52 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ExportComponent(object):
    def setupUi(self, ExportComponent):
        ExportComponent.setObjectName("ExportComponent")
        ExportComponent.resize(607, 88)
        ExportComponent.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout = QtGui.QHBoxLayout(ExportComponent)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.publishToLabel = QtGui.QLabel(ExportComponent)
        self.publishToLabel.setObjectName("publishToLabel")
        self.verticalLayout_2.addWidget(self.publishToLabel)
        self.assetTaskLabel = QtGui.QLabel(ExportComponent)
        self.assetTaskLabel.setObjectName("assetTaskLabel")
        self.verticalLayout_2.addWidget(self.assetTaskLabel)
        self.assetNameLabel = QtGui.QLabel(ExportComponent)
        self.assetNameLabel.setObjectName("assetNameLabel")
        self.verticalLayout_2.addWidget(self.assetNameLabel)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.publishToTaskLabel = QtGui.QLabel(ExportComponent)
        self.publishToTaskLabel.setText("")
        self.publishToTaskLabel.setObjectName("publishToTaskLabel")
        self.verticalLayout.addWidget(self.publishToTaskLabel)
        self.AssetTaskComboBox = QtGui.QComboBox(ExportComponent)
        self.AssetTaskComboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.AssetTaskComboBox.setObjectName("AssetTaskComboBox")
        self.verticalLayout.addWidget(self.AssetTaskComboBox)
        self.AssetNameLineEdit = QtGui.QLineEdit(ExportComponent)
        self.AssetNameLineEdit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.AssetNameLineEdit.setObjectName("AssetNameLineEdit")
        self.verticalLayout.addWidget(self.AssetNameLineEdit)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(ExportComponent)
        QtCore.QMetaObject.connectSlotsByName(ExportComponent)

    def retranslateUi(self, ExportComponent):
        ExportComponent.setWindowTitle(QtGui.QApplication.translate("ExportComponent", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.publishToLabel.setText(QtGui.QApplication.translate("ExportComponent", "Publish to:", None, QtGui.QApplication.UnicodeUTF8))
        self.assetTaskLabel.setText(QtGui.QApplication.translate("ExportComponent", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.assetNameLabel.setText(QtGui.QApplication.translate("ExportComponent", "AssetName:", None, QtGui.QApplication.UnicodeUTF8))

