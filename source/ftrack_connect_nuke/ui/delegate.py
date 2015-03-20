# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

import FnAssetAPI
from ftrack_connect_foundry.ui import delegate
import ftrack_connect_nuke.ui.knobs


def register_import_asset_dialog(parent_menu, connector):
    '''Register import asset dialog to *parent_menu* using *connector*.'''
    identifier  = 'ftrackImportAssetClass'

    from nukescripts import panels
    import ftrack_connect.ui.widget.import_asset

    globals()[identifier] = functools.partial(
        ftrack_connect.ui.widget.import_asset.FtrackImportAssetDialog,
        connector=connector
    )

    panels.registerWidgetAsPanel(
        '{0}.{1}'.format(__name__, identifier),
        'ftrackImportAsset',
        'ftrackDialogs.ftrackImportAssetDialog'
    )
    parent_menu.addCommand(
        'Import asset',
        'import ftrack_connect_nuke.ui.delegate;'
        'pane = nuke.getPaneFor("Properties.1");'
        'panel = nukescripts.restorePanel("ftrackDialogs.ftrackImportAssetDialog");'
        'panel.addToPane(pane)'
    )


def register_asset_manager_dialog(parent_menu, connector):
    '''Register asset manager dialog to *parent_menu* using *connector*.'''
    identifier  = 'ftrackAssetManagerDialogClass'

    from nukescripts import panels
    import ftrack_connect.ui.widget.asset_manager

    globals()[identifier] = functools.partial(
        ftrack_connect.ui.widget.asset_manager.FtrackAssetManagerDialog,
        connector=connector
    )

    panels.registerWidgetAsPanel(
        '{0}.{1}'.format(__name__, identifier),
        'ftrackAssetManager',
        'ftrackDialogs.ftrackAssetManagerDialog'
    )
    parent_menu.addCommand(
        'Asset manager',
        'import ftrack_connect_nuke.ui.delegate;'
        'pane = nuke.getPaneFor("Properties.1");'
        'panel = nukescripts.restorePanel("ftrackDialogs.ftrackAssetManagerDialog");'
        'panel.addToPane(pane)'
    )


def _create_info_view_menu(parent_menu):
    ''' Helper function to populate the *parent_menu* with the info view widgets.
    '''
    from ftrack_connect_foundry.ui.info_view import InfoView as _InfoView

    parent_menu.addCommand(
        _InfoView.getDisplayName(),
        'pane = nuke.getPaneFor("Properties.1");'
        'panel = nukescripts.restorePanel("{identifier}");'
        'panel.addToPane(pane)'.format(
            identifier=_InfoView.getIdentifier()
        )
    )


def _create_web_views(parent_menu):
    ''' Helper function to populate the *parent_menu* with the taskView and workingTaskInfoView.
    '''
    from ftrack_connect_foundry.ui.tasks_view import TasksView as _TasksView
    from ftrack_connect_foundry.ui.info_view import WorkingTaskInfoView as _WorkingTaskInfoView

    # Add Web Views located in the ftrack_connect_foundry package to the
    # menu for easier access.
    for widget in [_TasksView, _WorkingTaskInfoView]:
        parent_menu.addCommand(
            widget.getDisplayName(),
            'pane = nuke.getPaneFor("Properties.1");'
            'panel = nukescripts.restorePanel("{identifier}");'
            'panel.addToPane(pane)'.format(
                identifier=widget.getIdentifier()
            )
        )

class Delegate(delegate.Delegate):
    def __init__(self, bridge):
        super(Delegate, self).__init__(bridge)

        self.moduleName =  ".".join(__name__.split(".")[:-1])

    def populateMenu(self, menu):

        import nuke
        import legacy
        from nukescripts import panels
        from ftrack_connect_nuke.connector import Connector

        from ftrack_connect_nuke.ui.widget.publish_gizmo import GizmoPublisherDialog

        from ftrack_connect_nuke.ui.widget.publish_script import ScriptPublisherDialog
        from ftrack_connect_nuke.ui.widget.load_script import ScriptOpenerDialog
        Connector.registerAssets()


        # Populate the ui
        menu.addSeparator()

        # add ftrack publish node to the menu
        menu.addCommand('Create Publish Node', lambda: legacy.createFtrackPublish())

        register_import_asset_dialog(menu, Connector)
        register_asset_manager_dialog(menu, Connector)
        _create_info_view_menu(menu)

        menu.addSeparator()

        _create_web_views(menu)

        # Add new entries in the ftrack menu.
        menu.addSeparator()
        menu.addCommand('Publish gizmo', GizmoPublisherDialog)

        # The new load and publish script dialog's are waiting for some style
        # fixes.
        if False:
            menu.addCommand('Publish script', ScriptPublisherDialog)
            menu.addCommand('Load script', ScriptOpenerDialog)

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
            import nuke
            nukeMenu = nuke.menu("Nuke")
            menu = nukeMenu.addMenu("&ftrack")
            self.populateMenu(menu)
