# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AssetVersionDetails.ui'
#
# Created: Wed Jun 12 17:46:36 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AssetVersionDetails(object):
    def setupUi(self, AssetVersionDetails):
        AssetVersionDetails.setObjectName("AssetVersionDetails")
        AssetVersionDetails.resize(180, 424)
        AssetVersionDetails.setMinimumSize(QtCore.QSize(180, 0))
        AssetVersionDetails.setMaximumSize(QtCore.QSize(180, 16777215))
        self.horizontalLayout = QtGui.QHBoxLayout(AssetVersionDetails)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 75, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.AssetVersionImageLabel = QtGui.QLabel(AssetVersionDetails)
        self.AssetVersionImageLabel.setMinimumSize(QtCore.QSize(180, 120))
        self.AssetVersionImageLabel.setMaximumSize(QtCore.QSize(180, 120))
        self.AssetVersionImageLabel.setText("")
        self.AssetVersionImageLabel.setObjectName("AssetVersionImageLabel")
        self.verticalLayout.addWidget(self.AssetVersionImageLabel)
        self.AssetVersionDetailsLabel = QtGui.QLabel(AssetVersionDetails)
        self.AssetVersionDetailsLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.AssetVersionDetailsLabel.setWordWrap(True)
        self.AssetVersionDetailsLabel.setObjectName("AssetVersionDetailsLabel")
        self.verticalLayout.addWidget(self.AssetVersionDetailsLabel)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(AssetVersionDetails)
        QtCore.QMetaObject.connectSlotsByName(AssetVersionDetails)

    def retranslateUi(self, AssetVersionDetails):
        AssetVersionDetails.setWindowTitle(QtGui.QApplication.translate("AssetVersionDetails", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.AssetVersionDetailsLabel.setText(QtGui.QApplication.translate("AssetVersionDetails", "No asset selected", None, QtGui.QApplication.UnicodeUTF8))

