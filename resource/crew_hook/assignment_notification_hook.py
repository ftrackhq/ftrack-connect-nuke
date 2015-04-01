# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import shutil
import tempfile

import ftrack_legacy
import ftrack
import foundry.assetmgr.utils
import nuke

from FnAssetAPI import logging
import FnAssetAPI
from FnAssetAPI.decorators import ensureManager

import pprint

from ftrack_connect_nuke.ui.widget import crew

_session = ftrack.Session()


@ensureManager
def open_published_script(entity_reference):

    session = FnAssetAPI.SessionManager.currentSession()

    context = session.createContext()

    with context.scopedOverride():

        context.access = context.kRead
        context.locale = FnAssetAPI.specifications.DocumentLocale()

        path = session.resolveIfReference(entity_reference, context)

        # Make a temporary file copy to work around the save as issue.
        _, tf_suffix = os.path.splitext(path)

        tf = tempfile.NamedTemporaryFile(suffix='_v1{0}'.format(tf_suffix))
        shutil.copy2(path, tf.name)

        nuke.scriptClear()
        nuke.scriptOpen(tf.name)
        FnAssetAPI.logging.warning(tf.name)

        foundry.assetmgr.utils.storeTemporaryRootNodeData(
            'entityReference', entity_reference
        )

    return entity_reference


def callback(event):
    '''Handle assignment notification call to action.

    This hook will reset the environment variables TASK_ID and SHOT_ID to match
    the *event* and will try to load any nukescript published on the task.

    '''
    logging.info('Open nukescript published on task based on:\n{0}'.format(
        pprint.pformat(event['data']))
    )

    task_id = event['data']['task_id']
    task = _session.get('Task', task_id)

    logging.info('Setting FTRACK_TASKID to: {0}'.format(
        task_id
    ))

    os.environ['FTRACK_TASKID'] = task_id

    logging.info('Setting FTRACK_SHOTID to: {0}'.format(
        task_id
    ))
    os.environ['FTRACK_SHOTID'] = task['parent_id']

    # Find the component and open it in Nuke.

    components = _session.query(
        'select id, version.version from Component where '
        'name is "nukescript" and version.task_id is "{task_id}"'.format(
            task_id=task_id
        )
    ).all()

    components = sorted(
        components, key=lambda component: component['version']['version']
    )

    component = components[0]

    entity_reference = 'ftrack://{component_id}?entityType=component'.format(
        component_id=component['id']
    )

    open_published_script(entity_reference)

    if crew.crew_hub:
        data = crew.gather_crew_presence_data_from_environment()
        crew.crew_hub.updatePresence(data)


def register(registry, **kw):
    '''Register hook.'''

    logging.info('Register assignment notification hook')

    ftrack_legacy.EVENT_HUB.subscribe(
        'topic=ftrack.crew.notification.assignment',
        callback
    )
