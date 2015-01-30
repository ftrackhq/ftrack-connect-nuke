from PySide import QtCore, QtGui
from ImportOptions import Ui_ImportOptions
from StackedOptionsWidget import StackedOptionsWidget
from ftrack_connect_nuke import ftrackConnector


class ImportOptionsWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        super(ImportOptionsWidget, self).__init__(parent)
        self.ui = Ui_ImportOptions()
        self.ui.setupUi(self)

        self.stackedOptionsWidget = StackedOptionsWidget(self)

        xml = """<?xml version="1.0" encoding="UTF-8" ?>
                <options>
                    <assettype name="default">
                        <tab name="Options">
                            <row name="Import mode" accepts="maya">
                                <option type="radio" name="importMode">
                                    <optionitem name="Reference" value="True"/>
                                    <optionitem name="Import"/>
                                </option>
                            </row>
                            <row name="Preserve References" accepts="maya">
                                <option type="checkbox" name="mayaReference" value="True"/>
                            </row>
                            <row name="Add Asset Namespace" accepts="maya">
                                <option type="checkbox" name="mayaNamespace" value="False"/>
                            </row>
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
            if hasattr(assetClass, 'importOptions'):
                xmlExtraAssetTypes += '<assettype name="' + assetTypeStr + '">'
                xmlExtraAssetTypes += assetClass.importOptions()
                xmlExtraAssetTypes += '</assettype>'

        xml = xml.format(xmlExtraAssetTypes)

        self.stackedOptionsWidget.initStackedOptions(xml)
        self.ui.optionsPlaceHolderLayout.addWidget(self.stackedOptionsWidget)

    @QtCore.Slot(str)
    def setStackedWidget(self, stackName):
        self.stackedOptionsWidget.setCurrentPage(stackName)

    def getOptions(self):
        return self.stackedOptionsWidget.getOptions()
