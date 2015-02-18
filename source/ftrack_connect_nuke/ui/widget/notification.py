# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import urlparse

from PySide import QtGui

import nuke

import ftrack
from ftrack_connect.ui.widget import notification_list as _notification_list

from ftrack_connect_nuke.ftrackConnector.panelcom import (
    PanelComInstance as _PanelComInstance
)
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import (
    HeaderWidget
)


class Notification(QtGui.QDialog):

    def __init__(self, parent=None):
        '''Initialise widget with *parent*.'''
        super(Notification, self).__init__(parent=parent)

        self.setMinimumWidth(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
            )
        )

        self.central_widget = QtGui.QWidget(self)
        self.vertical_layout = QtGui.QVBoxLayout(self)
        self.horizontal_layout = QtGui.QHBoxLayout()

        self.header = HeaderWidget(self)
        self.header.setTitle('ftrack Notifications')

        self.vertical_layout.addWidget(self.header)

        self.notification_list = _notification_list.Notification(
            self.central_widget
        )

        self.horizontal_layout.addWidget(self.notification_list)
        self.vertical_layout.addLayout(self.horizontal_layout)

        self.setObjectName('ftrackNotification')
        self.setWindowTitle('ftrackNotification')

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
