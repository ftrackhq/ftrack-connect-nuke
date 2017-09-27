# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from QtExt import QtWidgets
from ftrack_connect_foundry.ui.info_view import InfoView
import nuke


class AssetInfoView(
    InfoView
):
    '''Display information about selected entity.'''

    _kIdentifier = 'com.ftrack.asset_information_panel'
    _kDisplayName = 'Asset Info'

    def render_info(self):
        '''Build and layout widget.'''
        layout = self.layout()
        label = QtWidgets.QLabel(
            '<h1><b>Please select an asset node.</b></h1>'
        )
        layout.addWidget(label)

    def __init__(self, bridge, parent=None):
        '''Initialise InvfoView.'''
        super(AssetInfoView, self).__init__(
            bridge, parent=parent
        )

        nodes = nuke.selectedNodes()

        if not nodes or not nodes[0]:
            self.render_info()
            return

        node = nodes[0]

        has_knob = node.knob('assetVersionId')
        if has_knob:

            asset_id = has_knob.value()
            asset_id = asset_id.split('ftrack://')[-1].split('?')[0]
            self.setEntityReference(asset_id)

        else:
            self.render_info()
            return
