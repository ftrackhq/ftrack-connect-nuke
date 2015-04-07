# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

# Import to bootstrap foundry api.
import ftrack_connect_nuke
import ftrack_connect
try:
    # Part of nuke 9.0dev < build 69
    import foundry.assetmgr
except:
    try:
        # Part of nuke 9.0dev >= build 69
        import nuke.assetmgr
    except:
        # included in ftrack-connect-foundry
        import assetmgr_nuke

try:
    # This is required to get build 76 to start.
    import nuke.assetmgr.host
except ImportError:
    pass

import nuke
