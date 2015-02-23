# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BrowseTasksSmall.ui'
#
# Created: Fri Sep 13 11:09:25 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_BrowseTasksSmall(object):
    def setupUi(self, BrowseTasksSmall):
        BrowseTasksSmall.setObjectName("BrowseTasksSmall")
        BrowseTasksSmall.resize(220, 49)
        self.verticalLayout = QtGui.QVBoxLayout(BrowseTasksSmall)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.shotLabel = QtGui.QLabel(BrowseTasksSmall)
        self.shotLabel.setMaximumSize(QtCore.QSize(75, 16777215))
        self.shotLabel.setObjectName("shotLabel")
        self.horizontalLayout.addWidget(self.shotLabel)
        self.browseTasksButton = QtGui.QPushButton(BrowseTasksSmall)
        self.browseTasksButton.setMinimumSize(QtCore.QSize(0, 27))
        self.browseTasksButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.browseTasksButton.setObjectName("browseTasksButton")
        self.horizontalLayout.addWidget(self.browseTasksButton)
        self.cancelButton = QtGui.QPushButton(BrowseTasksSmall)
        self.cancelButton.setEnabled(True)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 27))
        self.cancelButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.homeButton = QtGui.QPushButton(BrowseTasksSmall)
        self.homeButton.setMinimumSize(QtCore.QSize(27, 27))
        self.homeButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.homeButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.homeButton.setIcon(icon)
        self.homeButton.setIconSize(QtCore.QSize(18, 18))
        self.homeButton.setObjectName("homeButton")
        self.horizontalLayout.addWidget(self.homeButton)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 4)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(BrowseTasksSmall)
        QtCore.QObject.connect(self.browseTasksButton, QtCore.SIGNAL("clicked()"), BrowseTasksSmall.showHideTree)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), BrowseTasksSmall.closeTree)
        QtCore.QObject.connect(self.homeButton, QtCore.SIGNAL("clicked()"), BrowseTasksSmall.goHome)
        QtCore.QMetaObject.connectSlotsByName(BrowseTasksSmall)

    def retranslateUi(self, BrowseTasksSmall):
        BrowseTasksSmall.setWindowTitle(QtGui.QApplication.translate("BrowseTasksSmall", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.shotLabel.setText(QtGui.QApplication.translate("BrowseTasksSmall", "Shot: ", None, QtGui.QApplication.UnicodeUTF8))
        self.browseTasksButton.setText(QtGui.QApplication.translate("BrowseTasksSmall", "Select Task", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("BrowseTasksSmall", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import BrowseTasksSmall_rc
