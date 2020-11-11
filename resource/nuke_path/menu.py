# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

# Import to bootstrap foundry api.
import ftrack_connect_nuke
import ftrack_connector_legacy.config

ftrack_connector_legacy.config.configure_logging(
    'ftrack_connect_nuke', level='WARNING'
)
try:
    # part of nuke
    import foundry.assetmgr
except:
    # included in ftrack-connect-foundry
    import assetmgr_nuke

import nuke

import ftrack_connect_nuke.usage
import ftrack_connect_nuke.plugin
import ftrack_connect_nuke.logging


