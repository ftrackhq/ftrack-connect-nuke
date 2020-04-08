# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import ftrack_connect.config
from ._version import __version__

ftrack_connect.config.configure_logging(
    'ftrack_connect_nuke', level='WARNING'
)

import ftrack_connect_nuke.usage
import ftrack_connect_nuke.plugin
import ftrack_connect_nuke.logging

