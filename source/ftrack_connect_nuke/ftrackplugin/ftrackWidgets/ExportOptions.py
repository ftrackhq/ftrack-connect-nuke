# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportOptions.ui'
#
# Created: Wed Jul 17 17:18:21 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ExportOptions(object):
    def setupUi(self, ExportOptions):
        ExportOptions.setObjectName("ExportOptions")
        ExportOptions.resize(339, 266)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExportOptions.sizePolicy().hasHeightForWidth())
        ExportOptions.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(ExportOptions)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.optionsPlaceHolderLayout = QtGui.QHBoxLayout()
        self.optionsPlaceHolderLayout.setObjectName("optionsPlaceHolderLayout")
        self.verticalLayout.addLayout(self.optionsPlaceHolderLayout)
        self.label_4 = QtGui.QLabel(ExportOptions)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.thumbnailLineEdit = QtGui.QLineEdit(ExportOptions)
        self.thumbnailLineEdit.setObjectName("thumbnailLineEdit")
        self.gridLayout_4.addWidget(self.thumbnailLineEdit, 2, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(ExportOptions)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_4.addWidget(self.pushButton, 2, 1, 1, 1)
        self.screenshotButton = QtGui.QPushButton(ExportOptions)
        self.screenshotButton.setObjectName("screenshotButton")
        self.gridLayout_4.addWidget(self.screenshotButton, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_4)
        self.label_5 = QtGui.QLabel(ExportOptions)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.commentTextEdit = QtGui.QPlainTextEdit(ExportOptions)
        self.commentTextEdit.setMaximumSize(QtCore.QSize(16777215, 80))
        self.commentTextEdit.setObjectName("commentTextEdit")
        self.verticalLayout.addWidget(self.commentTextEdit)
        self.publishButton = QtGui.QPushButton(ExportOptions)
        self.publishButton.setObjectName("publishButton")
        self.verticalLayout.addWidget(self.publishButton)
        self.progressBar = QtGui.QProgressBar(ExportOptions)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.publishMessageLabel = QtGui.QLabel(ExportOptions)
        self.publishMessageLabel.setText("")
        self.publishMessageLabel.setObjectName("publishMessageLabel")
        self.verticalLayout.addWidget(self.publishMessageLabel)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ExportOptions)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), ExportOptions.setThumbnailFilename)
        QtCore.QObject.connect(self.screenshotButton, QtCore.SIGNAL("clicked()"), ExportOptions.takeScreenshot)
        QtCore.QMetaObject.connectSlotsByName(ExportOptions)

    def retranslateUi(self, ExportOptions):
        ExportOptions.setWindowTitle(QtGui.QApplication.translate("ExportOptions", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ExportOptions", "Thumbnail:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("ExportOptions", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.screenshotButton.setText(QtGui.QApplication.translate("ExportOptions", "Screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ExportOptions", "Comment:", None, QtGui.QApplication.UnicodeUTF8))
        self.publishButton.setText(QtGui.QApplication.translate("ExportOptions", "Publish!", None, QtGui.QApplication.UnicodeUTF8))

