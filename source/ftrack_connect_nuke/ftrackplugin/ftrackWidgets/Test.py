# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Test.ui'
#
# Created: Fri Mar 15 10:21:30 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import sys

from BrowseTasksWidget import BrowseTasksWidget
from BrowseTasksSmallWidget import BrowseTasksSmallWidget
from ListAssetsWidget import ListAssetsWidget
from ListAssetVersionsWidget import ListAssetVersionsWidget
from AssetVersionDetailsWidget import AssetVersionDetailsWidget
from WebViewWidget import WebViewWidget
from componentTableWidget import ComponentTableWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        #self.browseTasksWidget = BrowseTasksWidget(self)
        #self.browseTasksWidget.setGeometry(0, 0, 800, 600)
        #self.browseTasksWidget.hide()
        
        #self.horizontalLayout.addWidget(self.browseTasksWidget)
        
        #print MainWindow.height()
        #print MainWindow.width()
        self.browseTasksSmallWidget = BrowseTasksSmallWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.browseTasksSmallWidget)

        #self.listAssetsWidget = ListAssetsWidget(self.centralwidget)
        #self.horizontalLayout.addWidget(self.listAssetsWidget)

        #self.listAssetVersionsWidget = ListAssetVersionsWidget(self.centralwidget)
        #self.horizontalLayout.addWidget(self.listAssetVersionsWidget)

        #self.verticalLayout = QtGui.QVBoxLayout()
        #self.horizontalLayout.addLayout(self.verticalLayout)

        #self.listAssetVersionDetailsWidget = AssetVersionDetailsWidget(self.centralwidget)
        #self.verticalLayout.addWidget(self.listAssetVersionDetailsWidget)
        
        #self.importComponentWidget = ComponentTableWidget(self.centralwidget)
        #self.verticalLayout.addWidget(self.importComponentWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #QtCore.QObject.connect(self.browseTasksWidget, QtCore.SIGNAL('clickedShotSignal(QString)'), self.listAssetsWidget.updateView)
        #QtCore.QObject.connect(self.listAssetsWidget, QtCore.SIGNAL('clickedAssetSignal(QString)'), self.listAssetVersionsWidget.updateView)
        #QtCore.QObject.connect(self.listAssetVersionsWidget, QtCore.SIGNAL('clickedAssetVersionSignal(QString)'), self.listAssetVersionDetailsWidget.updateLabel)
        #QtCore.QObject.connect(self.listAssetVersionsWidget, QtCore.SIGNAL('clickedAssetVersionSignal(QString)'), self.importComponentWidget.updateComponentsTable)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # set up User Interface (widgets, layout...)
        self.setupUi(self)


# Main entry to program.  Sets up the main app and create a new window.
def main(argv):
    # create Qt application
    app = QtGui.QApplication(argv, True)
    # create main window
    wnd = MainWindow()  # classname
    wnd.show()
    # Start the app up
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main(sys.argv)
