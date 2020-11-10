# :coding: utf-8
# :copyright: Copyright (c) 2017 ftrack


import ftrack_connector_legacy_nuke
import ftrack_connector_legacy.usage


def send_event(event_name, metadata=None):
    '''Send usage information to server.'''

    import nuke

    if metadata is None:
        metadata = {
            'nuke_version': nuke.NUKE_VERSION_STRING,
            'ftrack_connector_legacy_nuke_version': ftrack_connector_legacy_nuke.__version__
        }

    ftrack_connector_legacy.usage.send_event(
        event_name, metadata
    )
