# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import urlparse
import getpass

from PySide import QtGui

import nuke
import ftrack_connect.crew_hub
import ftrack_connect.event_hub_thread
import ftrack
import ftrack_legacy
from ftrack_connect.ui.widget import notification_list as _notification_list
from ftrack_connect.ui.widget import crew as _crew

from ftrack_connect_nuke.ftrackConnector.panelcom import (
    PanelComInstance as _PanelComInstance
)
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import (
    HeaderWidget
)

# TODO: Move this to a proper place. Maybe where the Plugin is started?
eventHubThread = ftrack_connect.event_hub_thread.EventHubThread()
eventHubThread.start()

session = ftrack.Session()


class NukeCrewHub(ftrack_connect.crew_hub.SignalCrewHub):

    def isInterested(self, data):
        return True


class UserClassifier(object):
    '''Class to classify users based on your context.'''

    def __init__(self):
        '''Initialise classifier.'''
        super(UserClassifier, self).__init__()

        self._

    def __call__(self, user):
        '''Classify user and return relevant group.'''


class Crew(QtGui.QDialog):

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(Crew, self).__init__(parent=parent)

        self.setMinimumWidth(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
            )
        )

        self.vertical_layout = QtGui.QVBoxLayout(self)
        self.horizontal_layout = QtGui.QHBoxLayout()

        self.header = HeaderWidget(self)
        self.header.setTitle('Crew')

        self.vertical_layout.addWidget(self.header)

        self.notification_list = _notification_list.Notification(
            self
        )

        self._hub = NukeCrewHub()

        groups = ['Assigned', 'Supervisors']
        self.chat = _crew.Crew(
            groups, hub=self._hub, parent=self
        )

        for user in session.query(
            'select id, username, first_name, last_name'
            ' from User where is_active is True'
        ):
            if user['username'] != getpass.getuser():
                self.chat.addUser(
                    user['first_name'], user['id']
                )

        self.tab_panel = QtGui.QTabWidget(parent=self)
        self.tab_panel.addTab(self.chat, 'Chat')
        self.tab_panel.addTab(self.notification_list, 'Notifications')

        self.horizontal_layout.addWidget(self.tab_panel)

        # TODO: This styling should probably be done in a global stylesheet
        # for the entire Nuke plugin.
        self.notification_list.overlay.setStyleSheet('''
            BlockingOverlay {
                background-color: rgba(58, 58, 58, 200);
                border: none;
            }

            BlockingOverlay QFrame#content {
                padding: 0px;
                border: 80px solid transparent;
                background-color: transparent;
                border-image: none;
            }

            BlockingOverlay QLabel {
                background: transparent;
            }
        ''')

        self.notification_list.setStyleSheet('''
            QFrame {
                background-color: #2A2A2A;
                color: #969696;
            }

            QLabel {
                background-color: #323232;
            }

            QFrame#notification-list {
                border: 0;
                margin: 20px 0 0 0;
            }

            QFrame#notification-list QTableWidget {
                background-color: transparent;
                border: 0;
            }

            QFrame#notification-list QTableWidget::item {
                background-color: #323232;
                border-bottom: 1px solid #282828;
                padding: 0;
            }
        ''')

        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.addLayout(self.horizontal_layout)

        self.setObjectName('Crew')
        self.setWindowTitle('Crew')

        self._read_context_from_environment()

        panel_communication_singleton = _PanelComInstance.instance()
        panel_communication_singleton.addRefreshListener(
            self._read_context_from_environment
        )

        self._enter_chat()

    def _enter_chat(self):
        '''.'''
        user = ftrack_legacy.getUser(getpass.getuser())
        data = {
            'user': {
                'name': user.getName(),
                'id': user.getId()
            },
            'application': {
                'identifier': 'nuke',
                'label': 'Nuke {0}'.format(nuke.NUKE_VERSION_STRING)
            },
            'context': {
                'project_id': 'my_project_id',
                'containers': []
            }
        }

        self._hub.enter(data)

    def _update_notification_context(self):
        '''Update the notification list context on refresh.'''


    def _read_context_from_environment(self):
        '''Read context from environment.'''
        component_ids = []

        for node in nuke.allNodes():
            component_id = node.knob('componentId')
            if component_id and component_id.value():
                component_id = component_id.value()

                if 'ftrack://' in component_id:
                    url = urlparse.urlparse(component_id)
                    component_id = url.netloc
                component_ids.append(component_id)

        if component_ids:
            session = ftrack.Session()
            components = session.query(
                'select version.asset_id from Component where id in'
                ' ({0})'.format(','.join(component_ids))
            ).all()

            for component in components:
                self.notification_list.addContext(
                    component['version']['asset_id'], 'asset', False
                )

        self.notification_list.addContext(
            os.environ['FTRACK_SHOTID'], 'task', False
        )
        self.notification_list.addContext(
            os.environ['FTRACK_TASKID'], 'task', False
        )

        self.notification_list.reload()
