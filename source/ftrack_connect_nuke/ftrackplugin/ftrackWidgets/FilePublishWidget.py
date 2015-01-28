from PySide import QtCore, QtGui
from FilePublish import Ui_FilePublish
import ftrack


class FilePublishWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FilePublish()
        self.ui.setupUi(self)
        self.ui.filePublishTable.setColumnCount(2)
        self.ui.filePublishTable.setHorizontalHeaderLabels(['Filename', 'Componentname'])
        self.ui.filePublishTable.verticalHeader().setVisible(False)
        self.ui.filePublishTable.setColumnWidth(1, 150)
        self.ui.filePublishTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.filePublishTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.ui.filePublishTable.setTextElideMode(QtCore.Qt.ElideLeft)

    def setContent(self, contentArray):
        self.ui.filePublishTable.setRowCount(0)
        self.ui.filePublishTable.setRowCount(len(contentArray))

        rowCntr = 0
        for comp in contentArray:
            componentItem = QtGui.QTableWidgetItem()
            componentItem.setText(unicode(comp[0]))
            componentItem.setToolTip(comp[0])
            self.ui.filePublishTable.setItem(rowCntr, 0, componentItem)
            componentItem = QtGui.QTableWidgetItem()
            componentItem.setText(comp[1])
            componentItem.setToolTip(comp[1])
            self.ui.filePublishTable.setItem(rowCntr, 1, componentItem)
            rowCntr += 1
