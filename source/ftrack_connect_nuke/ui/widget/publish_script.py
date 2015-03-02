#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import os
# import re
# import ftrack
from PySide import QtGui
from FnAssetAPI import logging

from ftrack_connect_nuke.connector.nukeassets import NukeSceneAsset
# from ftrack_connect_nuke.connector.nukecon import Connector

from comment_widget import CommentWidget
from task_widgets import TaskWidget
from snapshots_widget import SnapshotsWidget
from base_dialog import BaseDialog
from ftrack_connect.ui.theme import applyTheme
from ftrack_connect.ui import resource


class ScriptPublisherDialog(BaseDialog):

    def __init__(self):
        # We need to set the activeWindow as parent to get the "refresh" button
        # for the snapshot working (For some reason it can't get it from a
        # default value..)
        super(ScriptPublisherDialog, self).__init__(
            QtGui.QApplication.activeWindow())
        # self.setFTrackTitle("Publish script...")
        applyTheme(self, 'integration')
        self._connectors_per_type = {}
        self._connectors_per_type['nuke_scene'] = NukeSceneAsset()
        self.setupUI()

        # Check error
        # if not self.is_error():
        self.initiate_tasks()
        # else:
        #     self.left_tasks_widget.setEnabled(False)
        #     self._asset_connectors_cbbox.setEnabled(False)
        #     self._snapshotWidget.setEnabled(False)
        #     self._comment_widget.setEnabled(False)
        #     self._tasks_btn.setEnabled(False)

        self.exec_()

    def setupUI(self):
        super(ScriptPublisherDialog, self).setupUI()

        self.resize(1300, 900)
        self.setMinimumWidth(1300)
        self.setMinimumHeight(900)

        # self.tasks_frame.setStyleSheet("background-color:grey;")

        # HEADER

        self.asset_conn_container = QtGui.QWidget(self.main_container)
        self.asset_conn_container_layout = QtGui.QHBoxLayout()
        self.asset_conn_container.setLayout(self.asset_conn_container_layout)
        # self.main_container_layout.addWidget(self.asset_conn_container)

        self.asset_conn_label = QtGui.QLabel('Type', self.main_container)
        self.asset_conn_label.setMinimumWidth(60)

        self.asset_conn_combo = QtGui.QComboBox(self.main_container)
        self.asset_conn_combo.setMinimumHeight(23)
        self.asset_conn_combo.addItems(self._connectors_per_type.keys())

        spacer_asset_type = QtGui.QSpacerItem(
            0,
            0,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum
        )

        self.asset_conn_container_layout.addWidget(self.asset_conn_label)
        self.asset_conn_container_layout.addWidget(self.asset_conn_combo)
        self.asset_conn_container_layout.addItem(spacer_asset_type)

        self.tasks_main_container_layout.addWidget(self.asset_conn_container)

        # Create "main content" for the publisher
        self.publish_container = QtGui.QWidget(self.main_container)
        self.publish_container_layout = QtGui.QHBoxLayout()
        self.publish_container.setLayout(self.publish_container_layout)

        self.main_container_layout.addWidget(self.publish_container)

        # Create "main content" splitter for the publisher
        self.publish_splitter = QtGui.QSplitter(self.publish_container)
        self.publish_splitter.setContentsMargins(0, 0, 0, 10)
        self.publish_splitter.setChildrenCollapsible(False)

        self.publish_container_layout.addWidget(self.publish_splitter)

        # Create left and right containers for the splitter
        self.publish_left_container = QtGui.QWidget(self.publish_splitter)
        self.publish_right_container = QtGui.QWidget(self.publish_splitter)

        self.publish_left_container_layout = QtGui.QVBoxLayout()
        self.publish_right_container_layout = QtGui.QVBoxLayout()

        self.publish_left_container.setLayout(
            self.publish_left_container_layout
        )
        self.publish_right_container.setLayout(
            self.publish_right_container_layout
        )

        # Left Splitter Container
        self.publish_left_container_layout.setContentsMargins(0, 0, 5, 0)

        self.left_tasks_widget = TaskWidget(self.publish_left_container)
        self.left_tasks_widget.set_read_only(False)
        self.left_tasks_widget.set_selection_mode(False)
        self.publish_left_container_layout.addWidget(self.left_tasks_widget)

        # Right Splitter Containers
        css_asset_version = "color: #de8888; font-weight: bold;"
        css_asset_global = """
        QFrame { padding: 3px; border-radius: 4px;
                 background: #222; color: #FFF; font-size: 13px; }
        QLabel { padding: 0px; background: none; }
        """

        self.right_top_container = QtGui.QFrame(self.publish_right_container)
        self.right_mid_container = QtGui.QFrame(self.publish_right_container)
        self.right_bot_container = QtGui.QFrame(self.publish_right_container)

        self.right_top_container.setStyleSheet(css_asset_global)
        self.right_mid_container.setStyleSheet(css_asset_global)
        self.right_bot_container.setStyleSheet(css_asset_global)

        self.right_top_container_layout = QtGui.QHBoxLayout()
        self.right_mid_container_layout = QtGui.QHBoxLayout()
        self.right_bot_container_layout = QtGui.QHBoxLayout()

        self.right_top_container.setLayout(self.right_top_container_layout)
        self.right_mid_container.setLayout(self.right_mid_container_layout)
        self.right_bot_container.setLayout(self.right_bot_container_layout)

        self.publish_right_container_layout.addWidget(self.right_top_container)
        self.publish_right_container_layout.addWidget(self.right_mid_container)
        self.publish_right_container_layout.addWidget(self.right_bot_container)

        # Right Splitter TOP Container
        asset_title_label = QtGui.QLabel('Asset', self.right_top_container)
        self._asset_name = QtGui.QLabel('..1', self.right_top_container)
        asset_spacer = QtGui.QSpacerItem(
            0,
            0,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum
        )
        version_title_label = QtGui.QLabel('Version', self.right_top_container)
        self._asset_version = QtGui.QLabel('..2', self.right_top_container)

        self._asset_name.setStyleSheet(css_asset_global)
        self._asset_version.setStyleSheet(css_asset_version)

        self.right_top_container_layout.addWidget(asset_title_label)
        self.right_top_container_layout.addWidget(self._asset_name)
        self.right_top_container_layout.addItem(asset_spacer)
        self.right_top_container_layout.addWidget(version_title_label)
        self.right_top_container_layout.addWidget(self._asset_version)

        # Right Splitter MID Container
        self._snapshotWidget = SnapshotsWidget(self.right_mid_container)
        self.right_mid_container_layout.addWidget(self._snapshotWidget)

        # Right Splitter BOT Container
        self._comment_widget = CommentWidget(self.right_bot_container)
        self.right_bot_container_layout.addWidget(self._comment_widget)

        self._connect_script_signals()
        self._save_btn.setText("Publish and Save script")
        # return

        # right_widget = QtGui.QWidget(splitter)
        # right_layout = QtGui.QVBoxLayout(right_widget)
        # right_layout.setContentsMargins(5, 0, 0, 0)
        # asset_frame = QtGui.QFrame(self)
        # asset_frame_layout = QtGui.QVBoxLayout(asset_frame)
        # asset_frame_layout.setContentsMargins(0, 0, 0, 0)
        # asset_frame_layout.setSpacing(10)

        # asset_main_frame = QtGui.QFrame(self)
        # asset_main_frame.setStyleSheet(css_asset_global)
        # asset_main_frame_layout = QtGui.QHBoxLayout(asset_main_frame)
        # asset_main_frame_layout.setSpacing(10)
        # asset_name_lbl = QtGui.QLabel("Asset", self)
        # self._asset_name = QtGui.QLabel("...", asset_frame)
        # self._asset_name.setStyleSheet(css_asset_name)
        # spacer_asset = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
        #                                  QtGui.QSizePolicy.Minimum)

        # asset_version_lbl = QtGui.QLabel("Version", asset_frame)
        # self._asset_version = QtGui.QLabel("...", asset_frame)
        # self._asset_version.setStyleSheet(css_asset_version)
        # asset_main_frame_layout.addWidget(asset_name_lbl)
        # asset_main_frame_layout.addWidget(self._asset_name)
        # asset_main_frame_layout.addItem(spacer_asset)
        # asset_main_frame_layout.addWidget(asset_version_lbl)
        # asset_main_frame_layout.addWidget(self._asset_version)
        # asset_frame_layout.addWidget(asset_main_frame)

        # asset_setting_layout = QtGui.QVBoxLayout()
        # asset_setting_layout.setContentsMargins(0, 0, 0, 0)
        # asset_setting_layout.setSpacing(10)
        # self._snapshotWidget = SnapshotsWidget(asset_frame)
        # asset_setting_layout.addWidget(self._snapshotWidget)

        # self._comment_widget = CommentWidget(asset_frame)
        # self._comment_widget.changed.connect(self._validate)
        # asset_setting_layout.addWidget(self._comment_widget)
        # asset_frame_layout.addItem(asset_setting_layout)

        # spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum,
        #                            QtGui.QSizePolicy.Expanding)
        # asset_frame_layout.addItem(spacer)

        # right_layout.addWidget(asset_frame)
        # splitter.addWidget(right_widget)

        # self.layout().addWidget(splitter)

        # self._save_btn.setMinimumWidth(150)

    def _connect_script_signals(self):
        self.asset_conn_combo.currentIndexChanged.connect(
            self._toggle_asset_type
        )

    @property
    def asset_thumbnail(self):
        return self._snapshotWidget.save_thumbnail()

    @property
    def comment(self):
        return self._comment_widget.text

    @property
    def asset_name(self):
        return self._asset_name.text()

    @property
    def connector(self):
        asset_type = self.asset_conn_combo.currentText()
        return self._connectors_per_type[asset_type]

    @property
    def current_shot_status(self):
        return self.left_tasks_widget.current_shot_status

    @property
    def current_asset_type(self):
        return self.asset_conn_combo.currentText()

    @property
    def current_task_status(self):
        return self.left_tasks_widget.current_task_status

    def current_shot_status_changed(self):
        return self.left_tasks_widget.current_shot_status_changed()

    def current_task_status_changed(self):
        return self.left_tasks_widget.current_task_status_changed()

    def _toggle_asset_type(self):
        # intermediary slot to ensure none of the signal argument is passed to the
        # "update_asset" method.

        self.update_asset()
        self._validate()

    def set_tasks(self):
        if self.current_task is not None:
            self.asset_conn_combo.blockSignals(True)

            # for i in range(self.asset_conn_combo.count()):
            #     asset_type = self.asset_conn_combo.itemText(i)
            #     connector = self._connectors_per_type[asset_type]

            #     #if connector.asset_type == self.current_task.getAsset():
            #     # self.asset_conn_combo.setCurrentIndex(i)

            self.asset_conn_combo.blockSignals(False)

            # If we are versioning a known asset, we can't set it on another
            # task
            # self.display_tasks_frame(False)   
            # self.set_header_command(
            #     "Show task list",
            #     "Hide task list",
            #     command=self.display_tasks_frame
            # )

        super(ScriptPublisherDialog, self).set_tasks()

    def update_task(self, *args):
        # task = self.current_task
        # if task is not None:
        #     logging.debug("current: %s" % task.getName())
        #     self.left_tasks_widget.set_task(task, self.current_task)
        #     self.update_asset()

        super(ScriptPublisherDialog, self).update_task(*args)
        self._comment_widget.setFocus()

    def update_asset(self):
        task = self.current_task
        asset_type = self.asset_conn_combo.currentText()
        # connector = self._connectors_per_type[asset_type]
        asset_name = task.getName() + "_" + asset_type
        self._asset_name.setText(asset_name)

        asset = self.current_task.getAssets(assetTypes=[asset_type])

        asset_version = 0
        if asset:
            asset = asset[0]
            version = asset.getVersions()
            if version:
                asset_version = version[-1].get('version')

        # version = task.asset_version_number(self.asset_name, self.connector.asset_type)
        self._asset_version.setText("%03d" % asset_version)

    def _validate(self, soft_validation=False):
        logging.debug("soft_validation: %s" % soft_validation)

        self.asset_conn_combo.setEnabled(True)
        # self.initiate_error_box()
        # self.initiate_warning_box()

        # Warning check

        warning = None

        asset_type = self.asset_conn_combo.currentText()
        connector = self._connectors_per_type[asset_type]
        if self.current_task != None and self.current_task != None:
            if self.current_task.getId() != self.current_task.getId():
                warning = "The current Nuke script doesn't belong to this task... The"
                "task should be '%s'" % self.current_task.getName()

            # elif self.current_task.connector.asset_type != connector.asset_type:
            #     warning = "The current Nuke script doesn't belong to this asset... The"
            #     "asset type should be '%s'" % self.current_task.connector.asset_type

        if warning is not None:
            self.set_warning(warning)
        else:
            self._validate_task()

        # Error check

        error = None
        display_error = True

        if self.current_task == None:
            error = "You don't have any task assigned to you."
            self.asset_conn_combo.setEnabled(False)

        elif self.current_task.getParent() == None:
            error = "This task isn't attached to any shot.. You need one to publish an asset"

        if error == None and len(self._comment_widget.text) == 0:
            error = "You must comment before publishing"
            if soft_validation:
                display_error = False

        if error != None:
            if display_error:
                self.set_error(error)
            else:
                self.set_enabled(False)
