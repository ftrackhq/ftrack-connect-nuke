# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import logging

import ftrack_legacy

log = logging.getLogger(__name__)


def callback(event):
    '''Handle property notification call to action.'''

    # TODO: Handle updated property values such as frame start and frame end.


def register(registry, **kw):
    '''Register hook.'''
    ftrack_legacy.EVENT_HUB.subscribe(
        'topic=ftrack.crew.notification.property',
        callback
    )
