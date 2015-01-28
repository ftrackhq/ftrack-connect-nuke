# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui
from ftrack_connect_foundry.ui import delegate
import legacy


class Delegate(delegate.Delegate):
    def __init__(self, bridge):
        super(Delegate, self).__init__(bridge)

        self.moduleName =  ".".join(__name__.split(".")[:-1])

    def populate_ftrack(self):
        import nuke
        FnAssetAPI.logging.info(self.moduleName)
        # add callbacks 
        nuke.addOnScriptLoad(legacy.refAssetManager)
        nuke.addOnScriptLoad(legacy.checkForNewAssets)


        # populate the toolbar
        toolbar = nuke.toolbar("Nodes")
        ftrackNodesMenu = toolbar.addMenu("ftrack", icon="logobox.png")
        ftrackNodesMenu.addCommand('ftrackPublish', '%s.legacy.createFtrackPublish()' % self.moduleName)

        # populate the ftrack menu
        ftrack_menu = nuke.menu("Nuke").findItem("ftrack")
        if not ftrack_menu:
            return       

        ftrack_menu.addCommand('Create Publish Node', '%s.legacy.createFtrackPublish()' % self.moduleName)


        # nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='Write')
        # nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='WriteGeo')
        # nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='Read')


        # nuke.addKnobChanged(legacy.ftrackPublishKnobChanged, nodeClass="Group")
        # nuke.addOnCreate(legacy.ftrackPublishHieroInit)


    def populateUI(self, uiElement, specification, context):
        super(Delegate, self).populateUI(uiElement, specification, context)

        host = FnAssetAPI.SessionManager.currentSession().getHost()

        if host and host.getIdentifier() == 'uk.co.foundry.nuke': 
            self.populate_ftrack()


            # fileMenu.addCommand("Save Comp", "os.environ",index=startingIndex)
            # versionUpMethod = "%s.utils._script_version_all_up()" % moduleName
            # versionUpTitle = "Save New &Version"
            # item = fileMenu.addCommand(versionUpTitle, versionUpMethod)