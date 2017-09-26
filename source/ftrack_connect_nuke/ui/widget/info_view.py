# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import traceback

from ftrack_connect_foundry.ui.info_view import InfoView
import nuke
import FnAssetAPI.logging
import FnAssetAPI.exceptions
import FnAssetAPI.ui.widgets
import ftrack

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
        if not node:
            return

        has_knob = node.knob('assetId')
        if not has_knob:
            return

        asset_id = has_knob.value()
        super(InfoView, self).__init__(
            bridge, parent=parent, entityReference=asset_id
        )

    def setEntityReference(self, entityReference):
        '''Display information about entity referred to by *entityReference*.'''
        entity = None
        if entityReference is not None:
            try:
                entity = self._bridge.getEntityById(entityReference)
                print 'ENTITY', entity
            except FnAssetAPI.exceptions.InvalidEntityReference:
                tb = traceback.format_exc()
                FnAssetAPI.logging.debug(tb)

        self.setEntity(entity)

    def setEntity(self, entity):
        '''Display information about specific *entity*.'''
        if entity is None:
            # TODO: Display nothing to display message.
            return

        if isinstance(entity, ftrack.Component):
            entity = entity.getVersion()

        if not self.getUrl():
            # Load initial page using url retrieved from entity.

            # TODO: Some types of entities don't have this yet, eg
            # assetversions. Add some checking here if it's not going to be
            # available from all entities.
            if hasattr(entity, 'getWebWidgetUrl'):
                url = entity.getWebWidgetUrl(name='info', theme='tf')
                FnAssetAPI.logging.debug(url)

                self.setUrl(url)

        else:
            # Send javascript to currently loaded page to update view.
            entityId = entity.getId()

            # NOTE: get('entityType') not supported on assetversions so
            # using private _type attribute.
            entityType = entity._type

            javascript = (
                'FT.WebMediator.setEntity({{'
                '   entityId: "{0}",'
                '   entityType: "{1}"'
                '}})'
                .format(entityId, entityType)
            )
            self.evaluateJavaScript(javascript)
