# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass
import sys
import pprint
import logging
import re
import os

import ftrack_api
import ftrack_connect.application

cwd = os.path.dirname(__file__)
sources = os.path.abspath(os.path.join(cwd, '..', 'dependencies'))
ftrack_connect_nuke_resource_path = os.path.abspath(os.path.join(
    cwd, '..',  'resource')
)
sys.path.append(sources)


import ftrack_connect_nuke


def on_discover_nuke_integration(session, event):

    entity = event['data']['context']['selection'][0]

    task = session.get('Context', entity['entityId'])

    nuke_connect_plugins = os.path.join(ftrack_connect_nuke_resource_path, 'nuke_path')

    data = {

        'integration': {
            "name": 'ftrack-connect-nuke',
            'version': ftrack_connect_nuke.__version__
        },

        'env': {
            'PYTHONPATH.prepend': sources,
            'NUKE_PATH': nuke_connect_plugins,
            'FOUNDRY_ASSET_PLUGIN_PATH': ftrack_connect_nuke_resource_path,
            'QT_PREFERRED_BINDING':  os.pathsep.join(['PySide2', 'PySide']),
            'NUKE_USE_FNASSETAPI': '1',
            'FTRACK_TASKID': task['id'],
            'FTRACK_SHOTID': task['parent']['id'],
            'LOGNAME.set': session._api_user,
            'FTRACK_APIKEY.set': session._api_key,
            'FS.set': task['parent']['id']['custom_attributes'].get('fstart', '1.0'),
            'FE.set': task['parent']['id']['custom_attributes'].get('fend', '100.0')
        }
    }
    return data