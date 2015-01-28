# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Applications.ui'
#
# Created: Thu Jun 20 11:17:55 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Applications(object):
    def setupUi(self, Applications):
        Applications.setObjectName("Applications")
        Applications.resize(400, 300)
        Applications.setAutoFillBackground(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Applications)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.verticalLayout_2.addLayout(self.mainLayout)

        self.retranslateUi(Applications)
        QtCore.QMetaObject.connectSlotsByName(Applications)

    def retranslateUi(self, Applications):
        Applications.setWindowTitle(QtGui.QApplication.translate("Applications", "Form", None, QtGui.QApplication.UnicodeUTF8))

import Application_rc
