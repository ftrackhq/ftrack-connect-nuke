# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportAssetOptions.ui'
#
# Created: Thu Jan 22 16:25:44 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ExportAssetOptions(object):
    def setupUi(self, ExportAssetOptions):
        ExportAssetOptions.setObjectName("ExportAssetOptions")
        ExportAssetOptions.resize(429, 130)
        self.verticalLayout = QtGui.QVBoxLayout(ExportAssetOptions)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.assetTaskLabel = QtGui.QLabel(ExportAssetOptions)
        self.assetTaskLabel.setMinimumSize(QtCore.QSize(120, 0))
        self.assetTaskLabel.setMaximumSize(QtCore.QSize(120, 16777215))
        self.assetTaskLabel.setObjectName("assetTaskLabel")
        self.gridLayout.addWidget(self.assetTaskLabel, 1, 0, 1, 1)
        self.ListAssetsComboBox = QtGui.QComboBox(ExportAssetOptions)
        self.ListAssetsComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.ListAssetsComboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.ListAssetsComboBox.setObjectName("ListAssetsComboBox")
        self.gridLayout.addWidget(self.ListAssetsComboBox, 0, 1, 1, 1)
        self.ListAssetNamesComboBox = QtGui.QComboBox(ExportAssetOptions)
        self.ListAssetNamesComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.ListAssetNamesComboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.ListAssetNamesComboBox.setObjectName("ListAssetNamesComboBox")
        self.gridLayout.addWidget(self.ListAssetNamesComboBox, 3, 1, 1, 1)
        self.AssetNameLineEdit = QtGui.QLineEdit(ExportAssetOptions)
        self.AssetNameLineEdit.setEnabled(True)
        self.AssetNameLineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.AssetNameLineEdit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.AssetNameLineEdit.setObjectName("AssetNameLineEdit")
        self.gridLayout.addWidget(self.AssetNameLineEdit, 4, 1, 1, 1)
        self.AssetTaskComboBox = QtGui.QComboBox(ExportAssetOptions)
        self.AssetTaskComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.AssetTaskComboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.AssetTaskComboBox.setObjectName("AssetTaskComboBox")
        self.gridLayout.addWidget(self.AssetTaskComboBox, 1, 1, 1, 1)
        self.labelAssetType = QtGui.QLabel(ExportAssetOptions)
        self.labelAssetType.setMinimumSize(QtCore.QSize(120, 0))
        self.labelAssetType.setMaximumSize(QtCore.QSize(120, 16777215))
        self.labelAssetType.setObjectName("labelAssetType")
        self.gridLayout.addWidget(self.labelAssetType, 0, 0, 1, 1)
        self.assetNameLabel = QtGui.QLabel(ExportAssetOptions)
        self.assetNameLabel.setMinimumSize(QtCore.QSize(120, 0))
        self.assetNameLabel.setMaximumSize(QtCore.QSize(120, 16777215))
        self.assetNameLabel.setObjectName("assetNameLabel")
        self.gridLayout.addWidget(self.assetNameLabel, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(ExportAssetOptions)
        self.label_2.setMinimumSize(QtCore.QSize(120, 0))
        self.label_2.setMaximumSize(QtCore.QSize(120, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.assetTaskLabel_2 = QtGui.QLabel(ExportAssetOptions)
        self.assetTaskLabel_2.setMinimumSize(QtCore.QSize(120, 0))
        self.assetTaskLabel_2.setMaximumSize(QtCore.QSize(120, 16777215))
        self.assetTaskLabel_2.setObjectName("assetTaskLabel_2")
        self.gridLayout.addWidget(self.assetTaskLabel_2, 2, 0, 1, 1)
        self.ListStatusComboBox = QtGui.QComboBox(ExportAssetOptions)
        self.ListStatusComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.ListStatusComboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.ListStatusComboBox.setObjectName("ListStatusComboBox")
        self.gridLayout.addWidget(self.ListStatusComboBox, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(ExportAssetOptions)
        QtCore.QObject.connect(self.ListAssetsComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), ExportAssetOptions.setFilter)
        QtCore.QObject.connect(self.ListAssetsComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), ExportAssetOptions.emitAssetType)
        QtCore.QMetaObject.connectSlotsByName(ExportAssetOptions)

    def retranslateUi(self, ExportAssetOptions):
        ExportAssetOptions.setWindowTitle(QtGui.QApplication.translate("ExportAssetOptions", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.assetTaskLabel.setText(QtGui.QApplication.translate("ExportAssetOptions", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.labelAssetType.setText(QtGui.QApplication.translate("ExportAssetOptions", "AssetType", None, QtGui.QApplication.UnicodeUTF8))
        self.assetNameLabel.setText(QtGui.QApplication.translate("ExportAssetOptions", "AssetName:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExportAssetOptions", "Existing Assets", None, QtGui.QApplication.UnicodeUTF8))
        self.assetTaskLabel_2.setText(QtGui.QApplication.translate("ExportAssetOptions", "Task status", None, QtGui.QApplication.UnicodeUTF8))

