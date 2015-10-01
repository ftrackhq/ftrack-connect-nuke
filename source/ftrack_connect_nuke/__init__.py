# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from ._version import __version__

# Setup ftrack as soon as possible to load plugins and connect to event server.
import ftrack
ftrack.setup()

import ftrack_connect_nuke.plugin
import ftrack_connect_nuke.logging
