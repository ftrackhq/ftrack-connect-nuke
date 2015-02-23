# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import urlparse
import random

from PySide import QtGui

import nuke

import ftrack
import ftrack_connect.ui.widget.user_presence


from ftrack_connect_nuke.ftrackConnector.panelcom import (
    PanelComInstance as _PanelComInstance
)
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import (
    HeaderWidget
)


class Presence(QtGui.QDialog):

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(Presence, self).__init__(parent=parent)
        self._groups = ('Assigned', 'Related', 'Contributors', 'Others')

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

        self.presence_widget = ftrack_connect.ui.widget.user_presence.UserPresence(
            self._groups, self
        )

        self.presence_widget.setStyleSheet('''
            QFrame {
                background-color: transparent;
                color: #969696;
            }

            QLabel {
                background-color: transparent;
            }

            QFrame#presence-list {
                border: 0;
                margin: 20px 0 0 0;
            }

            QFrame#presence-list QTableWidget {
                background-color: transparent;
                border: 0;
            }

            QFrame#presence-list QTableWidget::item {
                padding: 0;
            }

            QFrame#presence-list QTableWidget::item QWidget#header {
                color: #707070;
                font-weight: bold;
                margin-top: 20px;
                padding: 0;
            }

            QFrame#presence-list QTableWidget::item QLabel#name {
                color: white;
            }
        ''')

        self.horizontal_layout.addWidget(self.presence_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.addLayout(self.horizontal_layout)

        self.setObjectName('ftrackPresence')
        self.setWindowTitle('ftrackPresence')

        self._read_context_from_environment()

        panel_communication_singleton = _PanelComInstance.instance()
        panel_communication_singleton.addRefreshListener(
            self._read_context_from_environment
        )

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

        
        for component_id in component_ids:
            component = ftrack.Component(component_id)
            version = component.getVersion()
            user = version.getUser()
            self.presence_widget.addUser(
                user.getName(), user.getId(), 'Contributors'
            )

        for user in ftrack.Task(os.environ['FTRACK_TASKID']).getUsers():
            self.presence_widget.addUser(
                user.getName(), user.getId(), 'Assigned'
            )

        shot = ftrack.Task(os.environ['FTRACK_SHOTID'])
        for task in shot.getTasks():
            for user in task.getUsers():
                self.presence_widget.addUser(
                    user.getName(), user.getId(), 'Related'
                )
