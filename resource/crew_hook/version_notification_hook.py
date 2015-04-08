# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack_legacy
import ftrack
import nuke
from FnAssetAPI import logging
import pprint
import urlparse

from ftrack_connect.connector import FTAssetObject
from ftrack_connect_nuke.connector import Connector

_session = ftrack.Session()


def _getNodeName(assetId):
    '''Return node name in scene by *assetId*.'''
    nodes = {}

    for node in nuke.allNodes():
        assetIdKnob = node.knob('assetId')
        if assetIdKnob and assetIdKnob.value():
            nodes[assetIdKnob.value()] = node

    return nodes[assetId].name()


def callback(event):
    '''Handle version notification call to action.

    The callback will find the Node in the graph matching the parent asset of
    the version specified in `event['data']['version_id']`. When found it will
    try to match the Component used and replace it with a Component from the
    new version.

    '''
    logging.info('Changing version of asset based on data:\n{0}'.format(
        pprint.pformat(event['data']))
    )

    new_version = _session.query(
        'select components.id, components.name, id, asset.name, asset.id from '
        'AssetVersion where id is "{0}"'.format(event['data']['version_id'])
    ).all()[0]

    for node in nuke.allNodes():
        if node.Class() == 'Read':
            knob = node.knob('file')

            if (knob and knob.value() and 'ftrack://' in knob.value()):
                component_id = knob.value()

                url = urlparse.urlparse(component_id)
                component_id = url.netloc

                node_component = _session.query(
                    'select id, name, version.id, version.asset.id from '
                    'Component where id is "{0}"'.format(component_id)
                ).all()[0]

                if node_component['version']['asset']['id'] == new_version['asset']['id']:
                    logging.info('Found matching asset.')

                    # Update the value of the read node to match the new
                    # component.
                    for component in new_version['components']:

                        # Match the name to use the same component.
                        if component['name'] == node_component['name']:
                            knob.setValue(
                                'ftrack://{0}?entityType=component'.format(
                                    component['id']
                                )
                            )

                            return

    location = ftrack_legacy.Location('ftrack.connect')

    # TODO: See if this can be done by using the Locations API in the new
    # API.
    componentInLocation = location.getComponent(
        result['components'][0]['id']
    )

    accessPath = componentInLocation.getFilesystemPath()

    importObj = FTAssetObject(
        componentId=result['components'][0]['id'],
        filePath=accessPath,
        componentName=result['components'][0]['name'],
        assetVersionId=result['id']
    )

    Connector.changeVersion(
        iAObj=importObj,
        applicationObject=_getNodeName(result['asset']['id'])
    )


def register(registry, **kw):
    '''Register hook.'''

    logging.info('Register version notification hook')

    ftrack_legacy.EVENT_HUB.subscribe(
        'topic=ftrack.crew.notification.version',
        callback
    )
