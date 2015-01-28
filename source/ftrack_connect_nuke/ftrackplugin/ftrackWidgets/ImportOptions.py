# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportOptions.ui'
#
# Created: Tue Sep 17 17:16:30 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ImportOptions(object):
    def setupUi(self, ImportOptions):
        ImportOptions.setObjectName("ImportOptions")
        ImportOptions.resize(451, 16)
        self.verticalLayout = QtGui.QVBoxLayout(ImportOptions)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.optionsPlaceHolderLayout = QtGui.QHBoxLayout()
        self.optionsPlaceHolderLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.optionsPlaceHolderLayout.setObjectName("optionsPlaceHolderLayout")
        self.verticalLayout.addLayout(self.optionsPlaceHolderLayout)

        self.retranslateUi(ImportOptions)
        QtCore.QMetaObject.connectSlotsByName(ImportOptions)

    def retranslateUi(self, ImportOptions):
        ImportOptions.setWindowTitle(QtGui.QApplication.translate("ImportOptions", "Form", None, QtGui.QApplication.UnicodeUTF8))

