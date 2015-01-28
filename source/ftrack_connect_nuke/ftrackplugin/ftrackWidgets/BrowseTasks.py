# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BrowseTasks.ui'
#
# Created: Mon Apr  8 11:25:55 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_BrowseTasks(object):
    def setupUi(self, BrowseTasks):
        BrowseTasks.setObjectName("BrowseTasks")
        BrowseTasks.resize(946, 660)
        BrowseTasks.setAutoFillBackground(True)
        self.horizontalLayout = QtGui.QHBoxLayout(BrowseTasks)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.BrowseProjectComboBox = QtGui.QComboBox(BrowseTasks)
        self.BrowseProjectComboBox.setMaximumSize(QtCore.QSize(150, 30))
        self.BrowseProjectComboBox.setObjectName("BrowseProjectComboBox")
        self.verticalLayout.addWidget(self.BrowseProjectComboBox)
        self.BrowseTasksTreeView = QtGui.QTreeView(BrowseTasks)
        palette = QtGui.QPalette()
        self.BrowseTasksTreeView.setPalette(palette)
        self.BrowseTasksTreeView.setStyleSheet("")
        self.BrowseTasksTreeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.BrowseTasksTreeView.setIndentation(10)
        self.BrowseTasksTreeView.setObjectName("BrowseTasksTreeView")
        self.BrowseTasksTreeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.BrowseTasksTreeView)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(BrowseTasks)
        QtCore.QObject.connect(self.BrowseTasksTreeView, QtCore.SIGNAL("clicked(QModelIndex)"), BrowseTasks.updateAssetView)
        QtCore.QObject.connect(self.BrowseProjectComboBox, QtCore.SIGNAL("currentIndexChanged(QString)"), BrowseTasks.setProjectFilter)
        QtCore.QMetaObject.connectSlotsByName(BrowseTasks)

    def retranslateUi(self, BrowseTasks):
        BrowseTasks.setWindowTitle(QtGui.QApplication.translate("BrowseTasks", "Form", None, QtGui.QApplication.UnicodeUTF8))

