import os
from PySide import QtCore, QtGui
from ExportOptions import Ui_ExportOptions
from StackedOptionsWidget import StackedOptionsWidget
from ftrack_connect_nuke import ftrackConnector
import ftrack_legacy as ftrack


class ExportOptionsWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_ExportOptions()
        self.ui.setupUi(self)

        self.stackedOptionsWidget = StackedOptionsWidget(self)

        xml = self.getXml()

        self.stackedOptionsWidget.initStackedOptions(xml)
        self.ui.optionsPlaceHolderLayout.addWidget(self.stackedOptionsWidget)
        self.ui.progressBar.hide()

    def getXml(self):
        xml = """<?xml version="1.0" encoding="UTF-8" ?>
<options>
    <assettype name="default">
        <tab name="Options">
        </tab>
    </assettype>
    {0}
</options>
"""
        xmlExtraAssetTypes = ""
        assetHandler = ftrackConnector.FTAssetHandlerInstance.instance()
        assetTypesStr = sorted(assetHandler.getAssetTypes())
        for assetTypeStr in assetTypesStr:
            assetClass = assetHandler.getAssetClass(assetTypeStr)
            if hasattr(assetClass, 'exportOptions'):
                xmlExtraAssetTypes += '<assettype name="' + assetTypeStr + '">'
                xmlExtraAssetTypes += assetClass.exportOptions()
                xmlExtraAssetTypes += '</assettype>'

        xml = xml.format(xmlExtraAssetTypes)

        return xml
    
    def resetOptions(self):
        xml = self.getXml()
        self.stackedOptionsWidget.resetOptions(xml)

    @QtCore.Slot(str)
    def setStackedWidget(self, stackName):
        self.stackedOptionsWidget.setCurrentPage(stackName)

    def getOptions(self):
        return self.stackedOptionsWidget.getOptions()

    def getComment(self):
        return self.ui.commentTextEdit.toPlainText()

    def getThumbnail(self):
        return self.ui.thumbnailLineEdit.text()

    @QtCore.Slot()
    def setThumbnailFilename(self):
        shot = ftrack.Task(os.environ['FTRACK_SHOTID'])
        proj_root = shot.getProject().getRoot()
        fileName = QtGui.QFileDialog.getOpenFileName(self, \
                                                     self.tr("Open Image"), \
                                                     proj_root, \
                                                     self.tr("Image Files (*.png *.jpg *.jpeg"))
        self.ui.thumbnailLineEdit.setText(fileName[0])

    @QtCore.Slot()
    def takeScreenshot(self):
        fileName = ftrackConnector.Connector.takeScreenshot()
        self.ui.thumbnailLineEdit.setText(fileName)

    def setComment(self, comment):
        self.ui.commentTextEdit.clear()
        self.ui.commentTextEdit.appendPlainText(comment)

    def setProgress(self, progressInt):
        if not self.ui.progressBar.isVisible():
            self.ui.progressBar.show()
        self.ui.progressBar.setProperty("value", progressInt)
        if progressInt == 100:
            self.ui.progressBar.hide()

    def setMessage(self, message):
        self.ui.publishMessageLabel.setText(message)
