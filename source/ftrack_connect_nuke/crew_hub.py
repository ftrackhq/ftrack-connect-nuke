# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack_connect.crew_hub


class CrewHub(ftrack_connect.crew_hub.SignalCrewHub):

    def isInterested(self, data):
        '''Return if interested in user with *data*.'''

        # In first version we are interested in all users since all users
        # are visible in the list.
        return True

# Create global crew hub which can connect before UI is created.
_crew_hub = CrewHub()
