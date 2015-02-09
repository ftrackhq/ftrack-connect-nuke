#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui
import os, re

# from ..ftrack_io.task import N_TaskFactory
# from ..ftrack_io.asset import N_AssetFactory
# from ..ftrack_io.asset import AssetIOError

# from ..ftrack_io.assets.scene_io import SceneIO

from generic.base_dialog import BaseIODialog

from widgets.snapshots_widget import SnapshotsWidget
from widgets.comment_widget import CommentWidget
from task_widgets import TaskWidget

from FnAssetAPI import logging
from ftrack_connect_nuke.ftrackConnector.nukeassets import NukeSceneAsset
from ftrack_connect_nuke.ftrackConnector.nukecon import Connector


class ScriptPublisherDialog(BaseIODialog):
  def __init__(self, version_id):
    # We need to set the activeWindow as parent to get the "refresh" button for
    # the snapshot working (For some reason it can't get it from a default value..)
    super(ScriptPublisherDialog, self).__init__(QtGui.QApplication.activeWindow())
    self.setFTrackTitle("Publish script...")

    # self._scenes_connectors = Connector()

    self._connectors_per_type = {}
    # for scene_connector in self._scenes_connectors:
    self._connectors_per_type['nuke_scene'] = NukeSceneAsset()
    self.setupUI()

    # Check current asset (None if no version_id found)
    # try:
    #   self._current_scene = N_AssetFactory.get_asset_from_version_id(version_id, SceneIO)
    # except AssetIOError as err:
    #   self.set_error(str(err))

    # Check error
    if not self.is_error():
      self.initiate_tasks()
    else:
      self._task_widget.setEnabled(False)
      self._asset_connectors_cbbox.setEnabled(False)
      self._snapshotWidget.setEnabled(False)
      self._comment_widget.setEnabled(False)
      self._tasks_btn.setEnabled(False)

    self.exec_()

  def setupUI(self):
    # self.resize(1200,900)
    # self.setMinimumWidth(1200)
    # self.setMinimumHeight(900)

    # HEADER

    asset_connectors_layout = QtGui.QHBoxLayout()
    asset_connectors_layout.setSpacing(8)
    asset_connectors_lbl = QtGui.QLabel("Type", self._tasks_frame)
    asset_connectors_lbl.setMinimumWidth(60)
    self._asset_connectors_cbbox = QtGui.QComboBox(self._tasks_frame)
    self._asset_connectors_cbbox.setMinimumHeight(23)
    # self._asset_connectors_cbbox.addItems([c for c in self._scenes_connectors])
    self._asset_connectors_cbbox.addItems(self._connectors_per_type.keys())
    
    self._asset_connectors_cbbox.currentIndexChanged.connect(self._toggle_asset_type)
    spacer_asset_type = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                                QtGui.QSizePolicy.Minimum )
    asset_connectors_layout.addWidget(asset_connectors_lbl)
    asset_connectors_layout.addWidget(self._asset_connectors_cbbox)
    asset_connectors_layout.addItem(spacer_asset_type)

    self.addHeaderTaskItem(asset_connectors_layout)

    # CONTENT TASK

    # splitter = QtGui.QSplitter(self)
    # splitter.setContentsMargins(0,0,0,10)
    # splitter.setChildrenCollapsible(False)

    # left_widget = QtGui.QWidget(splitter)
    # left_layout = QtGui.QVBoxLayout(left_widget)
    # left_layout.setContentsMargins(0,0,5,0)
    # self._task_widget = TaskWidget(self)
    # self._task_widget.set_read_only(False)
    # self._task_widget.set_selection_mode(False)
    # left_layout.addWidget(self._task_widget)
    # splitter.addWidget(left_widget)

    # CONTENT ASSET

    css_asset_name = "color: #c3cfa4; font-weight: bold;"
    css_asset_version = "color: #de8888; font-weight: bold;"
    css_asset_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #222; color: #FFF; font-size: 13px; }
    QLabel { padding: 0px; background: none; }
    """

    css_comment = """
    QTextEdit { border: 3px solid #252525; }
    QScrollBar { border: 0; border-radius: 6px;
                 background-color: #333; margin: 1px;}
    QScrollBar::handle {background: #222; border: 1px solid #111;}
    QScrollBar::sub-line, QScrollBar::add-line {height: 0px; width: 0px;}
    """

    right_widget = QtGui.QWidget()
    right_layout = QtGui.QVBoxLayout(right_widget)
    right_layout.setContentsMargins(5,0,0,0)
    asset_frame = QtGui.QFrame(self)
    asset_frame_layout = QtGui.QVBoxLayout(asset_frame)
    asset_frame_layout.setContentsMargins(0,0,0,0)
    asset_frame_layout.setSpacing(10)

    asset_main_frame = QtGui.QFrame(self)
    asset_main_frame.setStyleSheet(css_asset_global)
    asset_main_frame_layout = QtGui.QHBoxLayout(asset_main_frame)
    asset_main_frame_layout.setSpacing(10)
    asset_name_lbl = QtGui.QLabel("Asset", self)
    self._asset_name = QtGui.QLabel("...", asset_frame)
    self._asset_name.setStyleSheet(css_asset_name)
    spacer_asset = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Minimum )

    asset_version_lbl = QtGui.QLabel("Version", asset_frame)
    self._asset_version = QtGui.QLabel("...", asset_frame)
    self._asset_version.setStyleSheet(css_asset_version)
    asset_main_frame_layout.addWidget(asset_name_lbl)
    asset_main_frame_layout.addWidget(self._asset_name)
    asset_main_frame_layout.addItem(spacer_asset)
    asset_main_frame_layout.addWidget(asset_version_lbl)
    asset_main_frame_layout.addWidget(self._asset_version)
    asset_frame_layout.addWidget(asset_main_frame)

    asset_setting_layout = QtGui.QVBoxLayout()
    asset_setting_layout.setContentsMargins(0,0,0,0)
    asset_setting_layout.setSpacing(10)
    self._snapshotWidget = SnapshotsWidget(asset_frame)
    asset_setting_layout.addWidget(self._snapshotWidget)

    self._comment_widget = CommentWidget(asset_frame)
    self._comment_widget.changed.connect(self._validate)
    asset_setting_layout.addWidget(self._comment_widget)
    asset_frame_layout.addItem(asset_setting_layout)

    spacer = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Minimum,
                                QtGui.QSizePolicy.Expanding )
    asset_frame_layout.addItem(spacer)

    right_layout.addWidget(asset_frame)
    # splitter.addWidget(right_widget)

    self.addContentWidget(right_widget)

    self._save_btn.setText("Publish and Save script")
    self._save_btn.setMinimumWidth(150)

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
    asset_type = self._asset_connectors_cbbox.currentText()
    return self._connectors_per_type[asset_type]

  @property
  def current_shot_status(self):
    return self._task_widget.current_shot_status

  @property
  def current_asset_type(self):
      return self._asset_connectors_cbbox.currentText()

  @property
  def current_task_status(self):
    return self._task_widget.current_task_status

  def current_shot_status_changed(self):
    return self._task_widget.current_shot_status_changed()

  def current_task_status_changed(self):
    return self._task_widget.current_task_status_changed()

  def _toggle_asset_type(self):
    # intermediary slot to ensure none of the signal argument is passed to the
    # "update_asset" method.

    self.update_asset()
    self._validate()

  def set_tasks(self):
    if self._current_scene != None:
      self._asset_connectors_cbbox.blockSignals(True)

      for i in range(self._asset_connectors_cbbox.count()):
        asset_type = self._asset_connectors_cbbox.itemText(i)
        connector = self._connectors_per_type[asset_type]

        if connector.asset_type == self._current_scene.connector.asset_type:
          self._asset_connectors_cbbox.setCurrentIndex(i)

      self._asset_connectors_cbbox.blockSignals(False)

      # If we are versioning a known asset, we can't set it on another task
      self.display_tasks_frame(False)
      self.set_header_command( "show task list", "hide task list",
                               command=self.display_tasks_frame )

    super(ScriptPublisherDialog, self).set_tasks()

  def update_task(self, *args):
    task = self.current_task
    if task != None:
      logging.debug("current: %s" % task.getName())
      # self._task_widget.set_task(task, self._current_scene)
      self.update_asset()

    self._validate(soft_validation=True)
    self._comment_widget.setFocus()

  def update_asset(self):
    task = self.current_task
    asset_type = self._asset_connectors_cbbox.currentText()
    connector = self._connectors_per_type[asset_type]
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

    self._asset_connectors_cbbox.setEnabled(True)
    self.initiate_error_box()
    self.initiate_warning_box()

    ### Warning check

    warning = None

    asset_type = self._asset_connectors_cbbox.currentText()
    connector = self._connectors_per_type[asset_type]
    if self.current_task != None and self._current_scene != None:
      if self._current_scene.task.id != self.current_task.id:
        warning = "The current Nuke script doesn't belong to this task... The \
task should be '%s'" % self._current_scene.task.parents
      elif self._current_scene.connector.asset_type != connector.asset_type:
        warning = "The current Nuke script doesn't belong to this asset... The \
asset type should be '%s'" % self._current_scene.connector.asset_type

    if warning != None:
      self.set_warning(warning)
    else:
      self._validate_task()

    ### Error check

    error = None
    display_error = True

    if  self.current_task == None:
      error = "You don't have any task assigned to you."
      self._asset_connectors_cbbox.setEnabled(False)

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
