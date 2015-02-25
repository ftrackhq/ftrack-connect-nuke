# Import to bootstrap foundry api.
import ftrack_connect_nuke
import ftrack_connect
try:
	# included in ftrack-connect-foundry
	import assetmgr_nuke
except:
	# part of nuke
	import foundry.assetmgr

import nuke
