# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import ftrack_connector_legacy.config
from ._version import __version__

ftrack_connector_legacy.config.configure_logging(
    'ftrack_connector_legacy_nuke', level='WARNING'
)

import ftrack_connector_legacy_nuke.usage
import ftrack_connector_legacy_nuke.plugin
import ftrack_connector_legacy_nuke.logging

