# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import ftrack_connect
from ._version import __version__

ftrack_connect.config.configure_logging(
    'ftrack_connect_maya', level='WARNING'
)

import ftrack_connect_nuke.usage
import ftrack_connect_nuke.plugin
import ftrack_connect_nuke.logging

