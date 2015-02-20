# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools
import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui
from ftrack_connect_foundry.ui import delegate

class Delegate(delegate.Delegate):
    def __init__(self, bridge):
        super(Delegate, self).__init__(bridge)

        self.moduleName =  ".".join(__name__.split(".")[:-1])

    def populate_ftrack(self):

        import nuke
        import legacy
        from nukescripts import panels
        from ftrack_connect_nuke.connector import Connector
        from ftrack_connect_nuke.millftrack_nuke.assets_manager import AssetsManager
        from ftrack_connect_nuke.millftrack_nuke.ui.gizmo_publisher_dialog import GizmoPublisherDialog
        
        Connector.registerAssets()

        # wrappers for initializing the widgets with the correct connector object
        def wrapImportAssetDialog(*args, **kwargs):
            from ftrack_connect.ui.widget.import_asset import FtrackImportAssetDialog
            return FtrackImportAssetDialog(connector=Connector)

        def wrapAssetManagerDialog(*args, **kwargs):
            from ftrack_connect.ui.widget.asset_manager import FtrackAssetManagerDialog
            return FtrackAssetManagerDialog(connector=Connector)


        millAssetManager = AssetsManager()

        # Populate the ui
        nukeMenu = nuke.menu("Nuke")
        ftrackMenu = nukeMenu.addMenu("&ftrack")

        # add ftrack publish node to the menu
        ftrackMenu.addCommand('Create ftrack Publish Node', lambda: legacy.createFtrackPublish())

        ftrackMenu.addSeparator()

        globals()['ftrackImportAssetClass'] = wrapImportAssetDialog

        panels.registerWidgetAsPanel(
            "%s.%s" % (__name__, 'ftrackImportAssetClass'),
            'ftrackImportAsset', 
            'ftrackDialogs.ftrackImportAssetDialog'
        )
        ftrackMenu.addCommand(
            'ImportAsset',
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("ftrackDialogs.ftrackImportAssetDialog");'
            'panel.addToPane(pane)'
        )
        
        globals()['ftrackAssetManagerDialogClass'] = wrapAssetManagerDialog

        # Create the asset manager dialog entry in the menu
        panels.registerWidgetAsPanel(
            "%s.%s" % (__name__, 'ftrackAssetManagerDialogClass'),
            'ftrackAssetManager', 
            'ftrackDialogs.ftrackAssetManagerDialog'
        )
        ftrackMenu.addCommand(
            'AssetManager',
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("ftrackDialogs.ftrackAssetManagerDialog");'
            'panel.addToPane(pane)'
        )


        # add new entries in the ftrack menu
        ftrackMenu.addSeparator()
        ftrackMenu.addCommand('Publish a gizmo...', millAssetManager.publish_gizmo_panel)
        ftrackMenu.addCommand('Publish script...', millAssetManager.publish_script_panel)
        ftrackMenu.addCommand('Load script...', millAssetManager.open_script_panel)

        # ftrackMenu.addCommand('Publish a group of nodes...', millAssetManager.publish_group_panel)

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

        file_menu = nukeMenu.menu('File')
        file_menu.addSeparator(index=7)
        file_menu.addCommand('FTrack - Open Script...', millAssetManager.open_script_panel, index=8)
        file_menu.addCommand('FTrack - Publish Script...', millAssetManager.publish_script_panel, index=8)
        file_menu.addCommand('FTrack - Publish a gizmo...', millAssetManager.publish_gizmo_panel, index=8)
        file_menu.addSeparator(index=8)

        # remove foundy ones
        fn_publish = file_menu.removeItem("Publish Script...")
        fn_open_publish = file_menu.removeItem("Open Published Script...")
        fn_publish_new = file_menu.removeItem("Publish Script to a New Version")

        
    def populateUI(self, uiElement, specification, context):
        super(Delegate, self).populateUI(uiElement, specification, context)

        host = FnAssetAPI.SessionManager.currentSession().getHost()

        if host and host.getIdentifier() == 'uk.co.foundry.nuke': 
            self.populate_ftrack()
