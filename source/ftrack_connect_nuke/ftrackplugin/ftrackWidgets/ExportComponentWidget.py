from PySide import QtCore, QtGui
from ExportComponent import Ui_ExportComponent
import ftrack


class ExportComponentWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_ExportComponent()
        self.ui.setupUi(self)

        self.ui.AssetTaskComboBoxModel = QtGui.QStandardItemModel()
        self.ui.AssetTaskComboBox.setModel(self.ui.AssetTaskComboBoxModel)

    @QtCore.Slot(str)
    def updateSettings(self, ftrackId):
        asset = ftrack.Asset(id)
        assetName = asset.getName()
        self.ui.AssetNameLineEdit.setText(assetName)

    @QtCore.Slot(str)
    def updateTasks(self, ftrackId):
        self.currentShotid = ftrackId
        try:
            task = ftrack.Task(ftrackId)
            shotpath = task.getName()

            taskParents = task.getParents()

            for parent in taskParents:
                shotpath = parent.getName() + '.' + shotpath

            self.ui.publishToTaskLabel.setText(shotpath)

            self.ui.AssetTaskComboBox.clear()
            tasks = task.getTasks()
            for task in tasks:
                assetTaskItem = QtGui.QStandardItem(task.getName())
                assetTaskItem.id = task.getId()
                self.ui.AssetTaskComboBoxModel.appendRow(assetTaskItem)
        except:
            print 'Not a task'

    def getShotId(self):
        return self.currentShotid

    def getTaskId(self):
        comboItem = self.ui.AssetTaskComboBoxModel.item(self.ui.AssetTaskComboBox.currentIndex())
        if comboItem:
            return comboItem.id
        else:
            return None

    def getAssetName(self):
        return self.ui.AssetNameLineEdit.text()
