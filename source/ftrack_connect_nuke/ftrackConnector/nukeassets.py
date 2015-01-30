import nukecon
import re
import glob

import nuke
import ftrack
import panelcom
import os
import traceback

from ftrack_connect_nuke.ftrackConnector.maincon import FTAssetHandlerInstance
from ftrack_connect_nuke.ftrackConnector.maincon import HelpFunctions
from maincon import FTAssetObject
from maincon import FTAssetType
from maincon import FTComponent

import assetmgr_nuke
import ftrack_connect_nuke.ftrackplugin.worker


class GenericAsset(FTAssetType):
    def __init__(self):
        super(GenericAsset, self).__init__()

    def importAsset(self, iAObj=None):
        return 'Imported generic asset'

    def publishAsset(self):
        return [], 'Generic publish not supported'

    def changeVersion(self, iAObj=None, applicationObject=None):
        #print 'changing'
        return True

    def addFTab(self, resultingNode):
        tab = nuke.Tab_Knob('ftrack')
        resultingNode.addKnob(tab)
        btn = nuke.String_Knob('componentId')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('componentName')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetVersionId')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetVersion')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetName')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetType')
        resultingNode.addKnob(btn)

    def setFTab(self, resultingNode, iAObj):
        if 'assetmgr_nuke' in globals():
            componentId = ftrack.Component(iAObj.componentId).getEntityRef()
            assetVersionId = ftrack.AssetVersion(iAObj.assetVersionId).getEntityRef()
        #    resultingNode.knob('file').setValue(componentId)
        else:
            componentId = iAObj.componentId
            assetVersionId = iAObj.assetVersionId
            
        #componentId = iAObj.componentId
        #assetVersionId = iAObj.assetVersionId
            
        resultingNode.knob('componentId').setValue(componentId)
        resultingNode.knob('componentName').setValue(iAObj.componentName)
        resultingNode.knob('assetVersionId').setValue(assetVersionId)
        resultingNode.knob('assetVersion').setValue(iAObj.assetVersion)
        resultingNode.knob('assetName').setValue(iAObj.assetName)
        resultingNode.knob('assetType').setValue(iAObj.assetType)


class ImageSequenceAsset(GenericAsset):
    def __init__(self):
        super(ImageSequenceAsset, self).__init__()

    def getStartEndFrames(self, iAObj):
        '''Return start and end from *iAObj*.'''
        component = ftrack.Component(iAObj.componentId)

        if component.getSystemType() == 'sequence':
            # Find out frame start and end from members if component
            # system type is sequence.
            members = component.getMembers()
            frames = [int(member.getName()) for member in members]
            start = min(frames)
            end = max(frames)
        else:
            start, end = HelpFunctions.getFileSequenceStartEnd(iAObj.filePath)

        return start, end

    def importAsset(self, iAObj=None):
        '''Create nuke read node from *iAObj.'''
        
        if iAObj.filePath.endswith('nk'):
            nuke.nodePaste(iAObj.filePath)
            return
        else:
            resultingNode = nuke.createNode('Read', inpanel=False)
            resultingNode['name'].setValue(iAObj.assetName + '_' + iAObj.componentName)

        self.addFTab(resultingNode)

        # Compute frame range
        # TODO: Store these attributes on the component for easy access.
        resultingNode['file'].fromUserText(iAObj.filePath)

        start, end = self.getStartEndFrames(iAObj)

        resultingNode['first'].setValue(start)
        resultingNode['origfirst'].setValue(start)
        resultingNode['last'].setValue(end)
        resultingNode['origlast'].setValue(end)

        proxyPath = ''
        assetVersion = ftrack.AssetVersion(iAObj.assetVersionId)
        try:
            proxyPath = assetVersion.getComponent(name='proxy').getImportPath()
        except:
            pass

        try:
            proxyPath = assetVersion.getComponent(name=iAObj.componentName + '_proxy').getImportPath()
        except:
            pass

        if proxyPath != '':
            resultingNode['proxy'].fromUserText(proxyPath)

        self.setFTab(resultingNode, iAObj)

        return 'Imported imgseq asset'

    def changeVersion(self, iAObj=None, applicationObject=None):
        n = nuke.toNode(applicationObject)
        #print assetVersionId
        proxyPath = ''
        try:
            proxyPath = ftrack.AssetVersion(iAObj.assetVersionId).getComponent(name='proxy').getImportPath()
        except:
            print 'No proxy'

        n['file'].fromUserText(iAObj.filePath)
        if proxyPath != '':
            n['proxy'].fromUserText(proxyPath)

        start, end = self.getStartEndFrames(iAObj)

        n['first'].setValue(start)
        n['origfirst'].setValue(start)
        n['last'].setValue(end)
        n['origlast'].setValue(end)

        self.setFTab(n, iAObj)

        return True
    
    def publishContent(self, content, assetVersion, progressCallback=None):

        publishedComponents = []

        for c in content:
            filename = c[0]
            componentName = c[1]

            sequenceComponent = FTComponent()

            start = int(float(c[2]))
            end = int(float(c[3]))

            if not start - end == 0:
                sequence_format = '{0} [{1}-{2}]'.format(
                    filename, start, end
                )
            else:
                sequence_format = '{0}'.format(
                    filename, start
                )

            sequenceIdentifier = sequence_format

            metaData = []

            if not '_proxy' in componentName:
                metaData.append(('img_main', 'True'))

            for meta in c[5]:
                metaData.append((meta[0], meta[1]))

            sequenceComponent.componentname = componentName
            sequenceComponent.path = sequenceIdentifier
            sequenceComponent.metadata = metaData

            publishedComponents.append(sequenceComponent)

        try:
            node = nuke.toNode(content[0][4])
            thumbnail = ftrackplugin.ftrackConnector.Connector.createThumbNail(node)
            print thumbnail
            if thumbnail:
                publishedComponents.append(FTComponent(componentname='thumbnail', path=thumbnail))
        except:
            print 'Failed to create thumbnail'
            import sys
            traceback.print_exc(file=sys.stdout)

        return publishedComponents
                    
    def publishAsset(self, iAObj=None):
        publishedComponents = []
        # needs rewrite with using publishContent
        return publishedComponents, 'image sequence asset published'


class CameraAsset(GenericAsset):
    def __init__(self):
        super(CameraAsset, self).__init__()

    def importAsset(self, iAObj=None):
        resultingNode = nuke.createNode("Camera2", inpanel=False)
        resultingNode['read_from_file'].setValue(True)
        resultingNode['file'].setValue(nukecon.Connector.windowsFixPath(iAObj.filePath))
        resultingNode['name'].setValue(iAObj.assetName)

        self.addFTab(resultingNode)
        self.setFTab(resultingNode, iAObj)

        return 'Imported camera asset'

    def changeVersion(self, iAObj=None, applicationObject=None):
        n = nuke.toNode(applicationObject)
        n['read_from_file'].setValue(True)
        n['file'].setValue(nukecon.Connector.windowsFixPath(iAObj.filePath))
        self.setFTab(n, iAObj)

        return True

    def publishContent(self, content, assetVersion, progressCallback=None):
        publishedComponents = []
        
        for c in content:
            publishfilename = c[0]
            componentName = c[1]
            
            publishedComponents.append(FTComponent(componentname=componentName, path=publishfilename))
            
        return publishedComponents

    def publishAsset(self, iAObj=None):
        return [], "Publish function not implemented for camera asset"
    

class GeometryAsset(GenericAsset):
    def __init__(self):
        super(GeometryAsset, self).__init__()

    def importAsset(self, iAObj=None):
        resultingNode = nuke.createNode("ReadGeo2", inpanel=False)
        resultingNode['file'].setValue(nukecon.Connector.windowsFixPath(iAObj.filePath))
        resultingNode['name'].setValue(iAObj.assetName)
        
        #fps = int(ftrack.Task(os.environ['FTRACK_SHOTID']).getFPS())
        #resultingNode['frame_rate'].setValue(fps)

        self.addFTab(resultingNode)
        self.setFTab(resultingNode, iAObj)

        return 'Imported geo asset'

    def changeVersion(self, iAObj=None, applicationObject=None):
        n = nuke.toNode(applicationObject)
        n['file'].setValue(nukecon.Connector.windowsFixPath(iAObj.filePath))
        self.setFTab(n, iAObj)

        return True

    def publishContent(self, content, assetVersion, progressCallback=None):
        publishedComponents = []
        
        for c in content:
            publishfilename = c[0]
            componentName = c[1]
            
            publishedComponents.append(FTComponent(componentname=componentName, path=publishfilename))
            
        return publishedComponents

    def publishAsset(self, iAObj=None):
        return [], "Publish function not implemented for geometry asset"


def registerAssetTypes():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name='cam', cls=CameraAsset)
    assetHandler.registerAssetType(name='img', cls=ImageSequenceAsset)
    assetHandler.registerAssetType(name='geo', cls=GeometryAsset)
