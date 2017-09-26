# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
from ftrack_connect_foundry.ui.info_view import InfoView
import nuke

from ftrack_connect.session import (
    get_shared_session
)

session = get_shared_session()


class AssetInfoView(
    InfoView
):
    '''Display information about selected entity.'''

    _kIdentifier = 'com.ftrack.asset_information_panel'
    _kDisplayName = 'Asset Info'

    def __init__(self, bridge, parent=None):
        '''Initialise InvfoView.'''
        node = nuke.selectedNodes()[0]
        print node
        asset_id = None
        super(InfoView, self).__init__(bridge, parent, asset_id)


    # def set_entity(self, entity):
    #     '''Display information about specific *entity*.'''
    #     if entity is None:
    #         return

    #     if entity.entity_type is 'Component':
    #         entity = entity.get('version')

    #     if not self.get_url():
    #         url = session.get_widget_url(
    #             'info', entity=entity, theme='tf'
    #         )

    #         # Load initial page using url retrieved from entity.
    #         self.set_url(
    #             url
    #         )

    #     else:
    #         # Send javascript to currently loaded page to update view.
    #         entityId = entity.get('id')

    #         entityType = ftrack_connect_nuke_studio.entity_reference.translate_to_legacy_entity_type(
    #             entity.entity_type
    #         )

    #         javascript = (
    #             'FT.WebMediator.setEntity({{'
    #             '   entityId: "{0}",'
    #             '   entityType: "{1}"'
    #             '}})'
    #             .format(entityId, entityType)
    #         )
    #         self.evaluateJavaScript(javascript)

    # def on_selection_changed(self, event):
    #     '''Handle selection changed events.'''
    #     selection = event.sender.selection()

    #     selection = [
    #         _item for _item in selection
    #         if isinstance(_item, hiero.core.TrackItem)
    #     ]

    #     if len(selection) != 1:
    #         return

    #     item = selection[0]
    #     entity = ftrack_connect_nuke_studio.entity_reference.get(
    #         item
    #     )

    #     if not entity:
    #         return

    #     self.set_entity(entity)