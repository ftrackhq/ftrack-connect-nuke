# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui
from ftrack_connect_foundry.ui import delegate
from ftrack_connect_foundry.ui.tasks_view import TasksView as _TasksView
from ftrack_connect_foundry.ui.info_view import (
    WorkingTaskInfoView as _WorkingTaskInfoView, InfoView as _InfoView
)
from ftrack_connect_nuke.ui.widget.presence import Presence

class Delegate(delegate.Delegate):
    def __init__(self, bridge):
        super(Delegate, self).__init__(bridge)

        self.moduleName =  ".".join(__name__.split(".")[:-1])

    def populate_ftrack(self):

        import nuke
        import legacy
        from nukescripts import panels
        from ftrack_connect_nuke import ftrackConnector
        from ftrack_connect_nuke.ftrackplugin.ftrackDialogs import ftrackAssetManagerDialog, ftrackImportAssetDialog
        
        ftrackConnector.Connector.registerAssets()

        # Populate the ui
        nukeMenu = nuke.menu("Nuke")
        ftrackMenu = nukeMenu.addMenu("&ftrack")

        ftrackMenu.addSeparator()

        # add ftrack publish node to the menu
        ftrackMenu.addCommand('Create Publish Node', lambda: legacy.createFtrackPublish())


        # Create the import asset dialog entry in the menu
        panels.registerWidgetAsPanel(
            'ftrack_connect_nuke.ftrackplugin.ftrackDialogs.ftrackImportAssetDialog.FtrackImportAssetDialog', 
            'ftrackImportAsset', 
            'ftrackDialogs.ftrackImportAssetDialog'
        )

        ftrackMenu.addSeparator()

        ftrackMenu.addCommand(
            'Import Asset',
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("ftrackDialogs.ftrackImportAssetDialog");'
            'panel.addToPane(pane)'
        )
        
        # Create the asset manager dialog entry in the menu
        panels.registerWidgetAsPanel(
            'ftrack_connect_nuke.ftrackplugin.ftrackDialogs.ftrackAssetManagerDialog.FtrackAssetManagerDialog', 
            'ftrackAssetManager', 
            'ftrackDialogs.ftrackAssetManagerDialog'
        )
        ftrackMenu.addCommand(
            'Asset Manager',
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("ftrackDialogs.ftrackAssetManagerDialog");'
            'panel.addToPane(pane)'
        )
        ftrackMenu.addCommand(
            _InfoView.getDisplayName(),
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("{identifier}");'
            'panel.addToPane(pane)'.format(
                identifier=_InfoView.getIdentifier()
            )
        )

        ftrackMenu.addSeparator()

        # Add Web Views located in the ftrack_connect_foundry package to the
        # menu for easier access.
        for widget in [_TasksView, _WorkingTaskInfoView]:
            ftrackMenu.addCommand(
                widget.getDisplayName(),
                'pane = nuke.getPaneFor("Properties.1");'
                'panel = nukescripts.restorePanel("{identifier}");'
                'panel.addToPane(pane)'.format(
                    identifier=widget.getIdentifier()
                )
            )

                # Create the notification dialog entry in the menu
        panels.registerWidgetAsPanel(
            'ftrack_connect_nuke.ui.widget.presence.Presence',
            'Crew',
            'widget.ftrackPresence'
        )
        ftrackMenu.addCommand(
            'Crew',
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("widget.ftrackPresence");'
            'panel.addToPane(pane)'
        )


        # Add ftrack publish node
        toolbar = nuke.toolbar("Nodes")
        ftrackNodesMenu = toolbar.addMenu("ftrack", icon="logobox.png")
        ftrackNodesMenu.addCommand('ftrackPublish', lambda: legacy.createFtrackPublish())

        # Set calbacks
        nuke.addOnScriptLoad(legacy.refAssetManager)
        nuke.addOnScriptLoad(legacy.checkForNewAssets)
        nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='Write')
        nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='WriteGeo')
        nuke.addOnUserCreate(legacy.addFtrackComponentField, nodeClass='Read')
        nuke.addKnobChanged(legacy.ftrackPublishKnobChanged, nodeClass="Group")
        nuke.addOnCreate(legacy.ftrackPublishHieroInit)


    def populateUI(self, uiElement, specification, context):
        super(Delegate, self).populateUI(uiElement, specification, context)

        host = FnAssetAPI.SessionManager.currentSession().getHost()

        if host and host.getIdentifier() == 'uk.co.foundry.nuke': 
            self.populate_ftrack()
