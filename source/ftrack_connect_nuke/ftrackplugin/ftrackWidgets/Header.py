# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Header.ui'
#
# Created: Wed Jul 17 17:14:20 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Header(object):
    def setupUi(self, Header):
        Header.setObjectName("Header")
        Header.resize(198, 35)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Header.sizePolicy().hasHeightForWidth())
        Header.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Header)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(9, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logoLabel = QtGui.QLabel(Header)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(21, 22))
        self.logoLabel.setMaximumSize(QtCore.QSize(21, 22))
        self.logoLabel.setText("")
        self.logoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/fbox.png"))
        self.logoLabel.setScaledContents(False)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout.addWidget(self.logoLabel)
        self.titleLabel = QtGui.QLabel(Header)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.horizontalLayout.addWidget(self.titleLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.helpButton = QtGui.QPushButton(Header)
        self.helpButton.setMinimumSize(QtCore.QSize(35, 35))
        self.helpButton.setMaximumSize(QtCore.QSize(35, 35))
        self.helpButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.helpButton.setIcon(icon)
        self.helpButton.setIconSize(QtCore.QSize(30, 30))
        self.helpButton.setFlat(True)
        self.helpButton.setObjectName("helpButton")
        self.horizontalLayout.addWidget(self.helpButton)

        self.retranslateUi(Header)
        QtCore.QObject.connect(self.helpButton, QtCore.SIGNAL("clicked()"), Header.openHelp)
        QtCore.QMetaObject.connectSlotsByName(Header)

    def retranslateUi(self, Header):
        Header.setWindowTitle(QtGui.QApplication.translate("Header", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.titleLabel.setText(QtGui.QApplication.translate("Header", "Title", None, QtGui.QApplication.UnicodeUTF8))

import HeaderResources_rc
