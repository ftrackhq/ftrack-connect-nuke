# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FileBrowser.ui'
#
# Created: Mon Sep  2 18:22:58 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FileBrowser(object):
    def setupUi(self, FileBrowser):
        FileBrowser.setObjectName("FileBrowser")
        FileBrowser.resize(887, 625)
        self.verticalLayout = QtGui.QVBoxLayout(FileBrowser)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(FileBrowser)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 25))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.currentPathLabel = QtGui.QLabel(self.widget)
        self.currentPathLabel.setObjectName("currentPathLabel")
        self.horizontalLayout_2.addWidget(self.currentPathLabel)
        self.pathLineEdit = QtGui.QLineEdit(self.widget)
        self.pathLineEdit.setObjectName("pathLineEdit")
        self.horizontalLayout_2.addWidget(self.pathLineEdit)
        self.sequenceCheckBox = QtGui.QCheckBox(self.widget)
        self.sequenceCheckBox.setChecked(True)
        self.sequenceCheckBox.setObjectName("sequenceCheckBox")
        self.horizontalLayout_2.addWidget(self.sequenceCheckBox)
        self.verticalLayout.addWidget(self.widget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dirTreeView = QtGui.QTreeView(FileBrowser)
        self.dirTreeView.setLineWidth(0)
        self.dirTreeView.setObjectName("dirTreeView")
        self.horizontalLayout.addWidget(self.dirTreeView)
        self.fileSequenceTableWidget = QtGui.QTableWidget(FileBrowser)
        self.fileSequenceTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.fileSequenceTableWidget.setShowGrid(False)
        self.fileSequenceTableWidget.setGridStyle(QtCore.Qt.NoPen)
        self.fileSequenceTableWidget.setObjectName("fileSequenceTableWidget")
        self.fileSequenceTableWidget.setColumnCount(0)
        self.fileSequenceTableWidget.setRowCount(0)
        self.horizontalLayout.addWidget(self.fileSequenceTableWidget)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 5)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FileBrowser)
        QtCore.QObject.connect(self.dirTreeView, QtCore.SIGNAL("clicked(QModelIndex)"), FileBrowser.updateFileViewer)
        QtCore.QObject.connect(self.pathLineEdit, QtCore.SIGNAL("returnPressed()"), FileBrowser.editPathPressed)
        QtCore.QObject.connect(self.sequenceCheckBox, QtCore.SIGNAL("clicked(bool)"), FileBrowser.toggleShowSequences)
        QtCore.QMetaObject.connectSlotsByName(FileBrowser)

    def retranslateUi(self, FileBrowser):
        FileBrowser.setWindowTitle(QtGui.QApplication.translate("FileBrowser", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.currentPathLabel.setText(QtGui.QApplication.translate("FileBrowser", "Path: ", None, QtGui.QApplication.UnicodeUTF8))
        self.pathLineEdit.setToolTip(QtGui.QApplication.translate("FileBrowser", "Pree Enter to go to path", None, QtGui.QApplication.UnicodeUTF8))
        self.sequenceCheckBox.setToolTip(QtGui.QApplication.translate("FileBrowser", "Group sequences of files into one entry", None, QtGui.QApplication.UnicodeUTF8))
        self.sequenceCheckBox.setText(QtGui.QApplication.translate("FileBrowser", "Sequence as one entry", None, QtGui.QApplication.UnicodeUTF8))

