# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Tasks.ui'
#
# Created: Tue Jun 18 12:40:20 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Tasks(object):
    def setupUi(self, Tasks):
        Tasks.setObjectName("Tasks")
        Tasks.resize(517, 445)
        self.verticalLayout = QtGui.QVBoxLayout(Tasks)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.allProjectsCheckBox = QtGui.QCheckBox(Tasks)
        self.allProjectsCheckBox.setChecked(True)
        self.allProjectsCheckBox.setObjectName("allProjectsCheckBox")
        self.horizontalLayout.addWidget(self.allProjectsCheckBox)
        self.showApprovedCheckBox = QtGui.QCheckBox(Tasks)
        self.showApprovedCheckBox.setChecked(False)
        self.showApprovedCheckBox.setObjectName("showApprovedCheckBox")
        self.horizontalLayout.addWidget(self.showApprovedCheckBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tasksTableWidget = QtGui.QTableWidget(Tasks)
        self.tasksTableWidget.setFrameShape(QtGui.QFrame.Box)
        self.tasksTableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.tasksTableWidget.setLineWidth(1)
        self.tasksTableWidget.setMidLineWidth(0)
        self.tasksTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tasksTableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tasksTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tasksTableWidget.setObjectName("tasksTableWidget")
        self.tasksTableWidget.setColumnCount(0)
        self.tasksTableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tasksTableWidget)

        self.retranslateUi(Tasks)
        QtCore.QObject.connect(self.tasksTableWidget, QtCore.SIGNAL("clicked(QModelIndex)"), Tasks.setCurrentTask)
        QtCore.QObject.connect(self.showApprovedCheckBox, QtCore.SIGNAL("clicked()"), Tasks.updateFilters)
        QtCore.QObject.connect(self.allProjectsCheckBox, QtCore.SIGNAL("clicked()"), Tasks.updateFilters)
        QtCore.QMetaObject.connectSlotsByName(Tasks)

    def retranslateUi(self, Tasks):
        Tasks.setWindowTitle(QtGui.QApplication.translate("Tasks", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.allProjectsCheckBox.setText(QtGui.QApplication.translate("Tasks", "Show All Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.showApprovedCheckBox.setText(QtGui.QApplication.translate("Tasks", "Show Done/Blocked", None, QtGui.QApplication.UnicodeUTF8))
        self.tasksTableWidget.setSortingEnabled(True)

