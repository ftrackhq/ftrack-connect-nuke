import sys
import nukescripts
import nuke
from nukescripts import panels
import tempfile
import traceback

import os
import maincon
from maincon import FTAssetHandlerInstance
from maincon import FTAssetObject
from maincon import HelpFunctions
from maincon import FTAssetType
from maincon import FTComponent

import ftrack
import nukeassets
import ftrack_connect_nuke.ftrackplugin.worker
from PySide import QtGui

try:
    import assetmgr_nuke
except:
    pass

import urlparse


def register_scheme(scheme):
    for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
        getattr(urlparse, method).append(scheme)

register_scheme('ftrack')


class Dialog(maincon.Dialog):
    def __init__(self):
        super(Dialog, self).__init__()
        self.dockName = 'myDock'

    def initGui(self):
        return None

    # Attach QT Gui to application
    def show(self):
        window = self.initGui()
        if self.type == 'panel':
            panels.registerWidgetAsPanel('ftrack_connect_nuke.ftrackplugin.ftrackDialogs.' + window.__name__, self.dockName, 'ftrackDialogs.' + self.__class__.__name__)
        elif self.type == 'popup':
            showWindow = window()
            showWindow.show()


class Connector(maincon.Connector):
    def __init__(self):
        super(Connector, self).__init__()

    @staticmethod
    def getAssets():
        allReadNodes = nuke.allNodes('Read')
        allCamNodess = nuke.allNodes('Camera2')
        allInterestingNodes = allReadNodes + allCamNodess

        componentIds = []

        for readNode in allInterestingNodes:
            try:
                valueftrackId = readNode.knob('componentId').value()
                if valueftrackId != '':
                    if 'ftrack://' in valueftrackId:
                        url = urlparse.urlparse(valueftrackId)
                        valueftrackId = url.netloc
                    componentIds.append((valueftrackId, readNode.name()))
            except:
                pass

        return componentIds

    @staticmethod
    def getFileName():
        return nuke.root().name()

    @staticmethod
    def getMainWindow():
        return None

    @staticmethod
    def importAsset(iAObj):
        # Check if this AssetName already exists in scene
        iAObj.assetName = Connector.getUniqueSceneName(iAObj.assetName)

        assetHandler = FTAssetHandlerInstance.instance()
        importAsset = assetHandler.getAssetClass(iAObj.assetType)
        if importAsset:
            result = importAsset.importAsset(iAObj)
            return result
        else:
            return 'assetType not supported'

    @staticmethod
    def selectObject(applicationObject='', clearSelection=True):
        if clearSelection:
            nukescripts.clear_selection_recursive()
        n = nuke.toNode(applicationObject)
        n.knob('selected').setValue(True)

    @staticmethod
    def selectObjects(selection):
        nukescripts.clear_selection_recursive()
        for obj in selection:
            Connector.selectObject(obj, clearSelection=False)

    @staticmethod
    def removeObject(applicationObject=''):
        deleteMeNode = nuke.toNode(applicationObject)
        nuke.delete(deleteMeNode)

    @staticmethod
    def changeVersion(applicationObject=None, iAObj=None):
        assetHandler = FTAssetHandlerInstance.instance()
        changeAsset = assetHandler.getAssetClass(iAObj.assetType)
        if changeAsset:
            result = changeAsset.changeVersion(iAObj, applicationObject)
            return result
        else:
            print 'assetType not supported'
            return False

    @staticmethod
    def getSelectedObjects():
        selection = nuke.selectedNodes()
        selectedObjects = []
        for node in selection:
            selectedObjects.append(node.name())
        return selectedObjects

    @staticmethod
    def getSelectedAssets():
        selection = nuke.selectedNodes()
        selectedObjects = []
        for node in selection:
            try:
                node.knob('componentId').value()
                selectedObjects.append(node.name())
            except:
                pass
        return selectedObjects

    @staticmethod
    def setNodeColor(applicationObject='', latest=True):
        # Green RGB 20, 161, 74
        # Orange RGB 227, 99, 22
        latestColor = int('%02x%02x%02x%02x' % (20, 161, 74, 255), 16)
        oldColor = int('%02x%02x%02x%02x' % (227, 99, 22, 255), 16)
        n = nuke.toNode(applicationObject)
        if latest:
            n.knob("note_font_color").setValue(latestColor)
        else:
            n.knob("note_font_color").setValue(oldColor)

    @staticmethod
    def publishAsset(iAObj=None):
        assetHandler = FTAssetHandlerInstance.instance()
        pubAsset = assetHandler.getAssetClass(iAObj.assetType)
        if pubAsset:
            publishedComponents, message = pubAsset.publishAsset(iAObj)
            #result = pubAsset.changeVersion(iAObj, applicationObject)
            return publishedComponents, message
        else:
            return [], 'assetType not supported'

    @staticmethod
    def init_dialogs(ftrackDialogs, availableDialogs=[]):
        nukeMenu = nuke.menu("Nuke")
        ftrackMenu = nukeMenu.addMenu("&ftrack")
        categories = dict()

        for dialog in availableDialogs:
            classObject = getattr(ftrackDialogs, dialog)
            accepts = classObject.accepts()
            category = classObject.category()
            connectorName = Connector.getConnectorName()
            if not accepts or connectorName in accepts:
                d = classObject()
                d.show()

                if category not in categories:
                    categories[category] = list()

                nukeMenuCommand = 'pane = nuke.getPaneFor("Properties.1")' + '\n'
                nukeMenuCommand += 'panel = nukescripts.restorePanel("ftrackDialogs.' + classObject.__name__ + '")' + '\n'
                nukeMenuCommand += 'panel.addToPane(pane)' + '\n'

                categories[category].append((dialog.replace('Dialog', '').replace('ftrack', ''), nukeMenuCommand))

        for category, menulist in sorted(categories.items()):
            for app in sorted(menulist, key=lambda entry: entry[1]):
                ftrackMenu.addCommand(app[0], app[1])

            ftrackMenu.addSeparator()

    @staticmethod
    def getConnectorName():
        return 'nuke'

    @staticmethod
    def getUniqueSceneName(assetName):
        res = nuke.toNode(assetName)
        if res:
            i = 0
            while res:
                uniqueAssetName = assetName + str(i)
                res = nuke.toNode(uniqueAssetName)
                i = i + 1
            return uniqueAssetName
        else:
            return assetName

    @classmethod
    def registerAssets(cls):
        nukeassets.registerAssetTypes()
        super(Connector, cls).registerAssets()

    @staticmethod
    def executeInThread(function, arg):
        nuke.executeInMainThreadWithResult(function, args=arg)

    # Create a thumbnail from the output of the nodeobject that is passed
    @staticmethod
    def createThumbNail(nodeObject):
        try:
            #test creating thumbnail
            reformatNode = nuke.nodes.Reformat()
            reformatNode['type'].setValue("to box")
            reformatNode['box_width'].setValue(200.0)
    
            reformatNode.setInput(0, nodeObject)
    
            w2 = nuke.nodes.Write()
            w2.setInput(0, reformatNode)
            thumbNailFilename = 'thumbnail_' + HelpFunctions.getUniqueNumber() + '.png'
            thumbnailDestination = os.path.join(tempfile.gettempdir(), thumbNailFilename)
            w2['file'].setValue(Connector.windowsFixPath(thumbnailDestination))
            w2['file_type'].setValue('png')

            curFrame = int(nuke.knob("frame"))
            nuke.execute(w2, curFrame, curFrame)
    
            nuke.delete(reformatNode)
            nuke.delete(w2)

            return thumbnailDestination
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            return None
        
    @staticmethod
    def windowsFixPath(path):
        path = path.replace('\\', '/')
        path = path.replace('\\\\', '/')
        return path