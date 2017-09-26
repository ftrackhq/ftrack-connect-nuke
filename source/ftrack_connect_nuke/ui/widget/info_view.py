# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from ftrack_connect_foundry.ui.info_view import InfoView
import nuke


class AssetInfoView(
    InfoView
):
    '''Display information about selected entity.'''

    _kIdentifier = 'com.ftrack.asset_information_panel'
    _kDisplayName = 'Asset Info'

    def __init__(self, bridge, parent=None):
        '''Initialise InvfoView.'''
        node = nuke.selectedNodes()[0]
        if not node:
            return

        has_knob = node.knob('componentId')
        if not has_knob:
            return

        asset_id = has_knob.value()
        asset_id = asset_id.split('ftrack://')[-1].split('?')[0]

        super(AssetInfoView, self).__init__(
            bridge, parent=parent, entityReference=asset_id
        )
