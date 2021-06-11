# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import sys
import os
import functools
import ftrack_api


cwd = os.path.dirname(__file__)
sources = os.path.abspath(os.path.join(cwd, '..', 'dependencies'))
ftrack_connect_nuke_resource_path = os.path.join(
    cwd, '..',  'resource')

sys.path.append(sources)


def on_discover_nuke_integration(session, event):

    from ftrack_connect_nuke import __version__ as integration_version
    data = {
        'integration': {
            'name': 'ftrack-connect-nuke',
            'version': integration_version
        }
    }

    return data


def on_launch_nuke_integration(session, event):
    nuke_base_data = on_discover_nuke_integration(session, event)

    nuke_connect_plugins = os.path.join(ftrack_connect_nuke_resource_path, 'nuke_path')


    nuke_base_data['integration']['env'] = {
        'PYTHONPATH.prepend': sources,
        'NUKE_PATH': nuke_connect_plugins,
        'FOUNDRY_ASSET_PLUGIN_PATH': ftrack_connect_nuke_resource_path,
        'QT_PREFERRED_BINDING':  os.pathsep.join(['PySide2', 'PySide']),
        'NUKE_USE_FNASSETAPI': '1',
        'LOGNAME.set': session._api_user,
        'FTRACK_APIKEY.set': session._api_key,
    }

    selection = event['data'].get('context', {}).get('selection', [])
    
    if selection:
        task = session.get('Context', selection[0]['entityId'])
        nuke_base_data['integration']['env']['FTRACK_TASKID.set'] =  task['id']
        nuke_base_data['integration']['env']['FTRACK_SHOTID.set'] =  task['parent']['id']
        nuke_base_data['integration']['env']['FS.set'] = task['parent']['custom_attributes'].get('fstart', '1.0'),
        nuke_base_data['integration']['env']['FE.set'] = task['parent']['custom_attributes'].get('fend', '100.0')

    return nuke_base_data



def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_discovery_event = functools.partial(
        on_discover_nuke_integration,
        session
    )
    
    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover'
        ' and data.application.identifier=nuke_*'
        ' and data.application.version < 13.0',
        handle_discovery_event
    )

    handle_launch_event = functools.partial(
        on_launch_nuke_integration,
        session
    )    

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch'
        ' and data.application.identifier=nuke_*'
        ' and data.application.version < 13.0',
        handle_launch_event
    )

