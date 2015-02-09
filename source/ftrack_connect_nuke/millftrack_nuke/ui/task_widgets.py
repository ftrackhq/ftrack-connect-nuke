#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftrack
from PySide import QtGui, QtCore, QtWebKit
import os, datetime

from widgets.assets_tree import AssetsTree
from generic.dockable_widget import BaseDockableWidget

from widgets.status_widget import StatusWidget

from ..controller import Controller

# from ..ftrack_io.asset import N_AssetFactory

# from ..ftrack_io.task import TaskIO
# from ..ftrack_io.asset import AssetVersionIO
# from ..ftrack_io.asset import AssetIOError

# from ..ftrack_io.assets.scene_io import SceneIO

from FnAssetAPI import logging

import nuke


class TaskManagerWidget(BaseDockableWidget):
  def __init__(self, parent=None):
    super(TaskManagerWidget, self).__init__(parent)
    self.setupUI()

    nuke.addOnScriptLoad( self.refresh )
    nuke.addOnScriptSave( self.refresh )

    self.refresh()

  def setupUI(self):
    self.setMinimumWidth(400)

    widget = QtGui.QWidget(self)
    main_layout = QtGui.QVBoxLayout(widget)
    main_layout.setContentsMargins(0,0,0,0)
    main_layout.setSpacing(0)

    self._webview = QtWebKit.QWebView()
    self._webview_empty = QtWebKit.QWebView()

    self._stackLayout = QtGui.QStackedLayout()
    self._stackLayout.addWidget(self._webview)
    self._stackLayout.addWidget(self._webview_empty)
    main_layout.addLayout(self._stackLayout)

    self._stackLayout.setCurrentWidget(self._webview_empty)
    self.addContentWidget(widget)

    self._refresh_btn = QtGui.QPushButton("Refresh", widget)
    self._refresh_btn.clicked.connect(self.refresh)
    self.addContentWidget(self._refresh_btn)

  def _get_meta(self, knob_name):
    if knob_name in nuke.root().knobs().keys():
      return nuke.root()[knob_name].value()

  def refresh(self):
    self.initiate_error_box()

    version_id = self._get_meta("ftrack_version_id")
    if version_id == None:
      msg = "This script is not an asset and does not belong to any tasks. "
      msg += "Please publish it in order to manage the corresponding task. "
      detail = "File > Mill Ftrack - Publish Script"
      self.set_error(msg, detail)
      self._stackLayout.setCurrentWidget(self._webview_empty)
      return

    try:
      current_scene = N_AssetFactory.get_asset_from_version_id(version_id, SceneIO)
    except AssetIOError as err:
      msg = "The Version Asset ID of this script is incorrect. Please contact RnD."
      detail = "Version Asset ID : %s\nError: %s" % (version_id, str(err))
      self.set_error(msg, detail)
      self._stackLayout.setCurrentWidget(self._webview_empty)
      return

    url = QtCore.QUrl(current_scene.task.web_widget_infos_Url)
    if not url.isValid():
      msg = "The task Url 'info' is incorrect."
      self.set_error(msg)
      self._stackLayout.setCurrentWidget(self._webview_empty)
      return

    self._webview.load(url)
    self._stackLayout.setCurrentWidget(self._webview)


class TaskWidget(QtGui.QWidget):
  asset_version_selected = QtCore.Signal(object)
  no_asset_version = QtCore.Signal()

  def __init__(self, parent=None):
    super(TaskWidget, self).__init__(parent)
    self.setupUI()

    self._current_task = None 

    self._read_only = True
    self._selection_mode = False

    self._tasks_dict = dict()

  def setupUI(self):
    main_layout = QtGui.QVBoxLayout(self)
    main_layout.setContentsMargins(0,0,0,0)
    main_layout.setSpacing(0)

    empty_task = SingleTaskWidget(parent=self)
    self._stackLayout = QtGui.QStackedLayout()
    self._stackLayout.addWidget(empty_task)
    main_layout.addLayout(self._stackLayout)

    self._stackLayout.setCurrentWidget(empty_task)

  @property
  def current_shot_status(self):
    single_task_widget = self._stackLayout.currentWidget()
    return single_task_widget._shot_status.status

  @property
  def current_task_status(self):
    single_task_widget = self._stackLayout.currentWidget()
    return single_task_widget._task_status.status

  @property
  def current_asset_version(self):
    if self._current_task != None and self._selection_mode:
      widget = self._tasks_dict[self._current_task.parents]
      tree = widget.assets_widget.assets_tree
      return tree.current_version

  def set_read_only(self, bool_value):
    self._read_only = bool_value
    for widget in self._tasks_dict.values():
      widget.set_read_only(bool_value)

  def set_selection_mode(self, bool_value):
    self._selection_mode = bool_value
    for widget in self._tasks_dict.values():
      widget.set_selection_mode(bool_value)

  def _get_task_parents(self, task):
      parents = [t.getName() for t in task.getParents()]
      parents.reverse()
      parents.append(task.getName())
      parents = ' / '.join(parents)
      return parents
      
  def set_task(self, task, current_scene=None):
    parents = self._get_task_parents(task)
    if parents not in self._tasks_dict.keys():
      single_task_widget = SingleTaskWidget(task, current_scene, self)
      single_task_widget.assets_widget.assets_tree.asset_version_selected.connect(self._emit_asset_version_selected)
      single_task_widget.set_read_only(self._read_only)
      single_task_widget.set_selection_mode(self._selection_mode)
      self._tasks_dict[parents] = single_task_widget
      self._stackLayout.addWidget(single_task_widget)

    self._stackLayout.setCurrentWidget(self._tasks_dict[parents])
    self._current_task = task

  def current_shot_status_changed(self):
    single_task_widget = self._stackLayout.currentWidget()
    return single_task_widget._shot_status.status_changed()

  def current_task_status_changed(self):
    single_task_widget = self._stackLayout.currentWidget()
    return single_task_widget._task_status.status_changed()

  def _emit_asset_version_selected(self, asset_version):
    self.asset_version_selected.emit(asset_version)


class SingleTaskWidget(QtGui.QFrame):

  def __init__(self, task=None, current_scene=None, parent=None):
    super(SingleTaskWidget, self).__init__(parent)

    self._task = task
    self._current_scene = current_scene

    # task infos
    self._t_project_name = "loading..."
    self._t_sequence_name = None
    self._t_shot_name = None
    self._t_shot_status = None
    self._t_name = "loading..."
    self._t_status = None
    self._t_due_date = None

    self.setupUI()

    # Thread that...
    self._controller = Controller(self._get_task_infos)
    self._controller.completed.connect(self.initiate_task)
    self._controller.start()

  def setupUI(self):
    css_task_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #252525; color: #FFF; }
    QLabel { padding: 0px; background: none; }
    QTabWidget::pane { border-top: 2px solid #151515; top: -2px;}
    QTabBar::tab { padding: 6px 10px; background: #151515;
                   border-top: 2px solid #151515;
                   border-right: 2px solid #151515;
                   border-left: 2px solid #151515;
                   border-radius: 0px; }
    QTabBar::tab:selected { background: #333;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px; }
    QTabBar::tab:hover { background: #222; }
    QTabBar::tab:!selected { margin-top: 2px; }
    """
    css_task_name_lbl = "font-size: 13px;"
    css_task_name = "color: #c3cfa4; font-size: 13px; font-weight: bold;"

    self.setStyleSheet(css_task_global)

    task_frame_layout = QtGui.QVBoxLayout(self)
    task_frame_layout.setContentsMargins(0,0,0,0)
    task_frame_layout.setSpacing(15)

    ## Display Task infos

    task_info_layout = QtGui.QFormLayout()
    task_info_layout.setContentsMargins(10,10,10,10)
    task_info_layout.setSpacing(10)

    task_name_lbl = QtGui.QLabel("Task", self)
    task_name_lbl.setStyleSheet(css_task_name_lbl)
    self._task_name = QtGui.QLabel(self._t_name, self)
    self._task_name.setStyleSheet(css_task_name)

    project_lbl = QtGui.QLabel("Project", self)
    self._project_name = QtGui.QLabel(self._t_project_name, self)

    shot_lbl = QtGui.QLabel("Shot", self)
    shot_layout = QtGui.QHBoxLayout()
    shot_layout.setSpacing(6)
    self._shot_name = QtGui.QLabel(self)
    self._separator_shot = QtGui.QLabel("/", self)
    self._separator_shot.setVisible(False)
    self._sequence_name = QtGui.QLabel(self)
    spacer_shot = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                           QtGui.QSizePolicy.Minimum )
    shot_layout.addWidget(self._sequence_name)
    shot_layout.addWidget(self._separator_shot)
    shot_layout.addWidget(self._shot_name)
    shot_layout.addItem(spacer_shot)

    shot_status_lbl = QtGui.QLabel("Shot status", self)
    shot_status = ftrack.getShotStatuses()
    self._shot_status = StatusWidget(shot_status, self)

    task_status_lbl = QtGui.QLabel("Task status", self)
    task_status = ftrack.getTaskStatuses()
    self._task_status = StatusWidget(task_status, self)

    due_date_lbl = QtGui.QLabel("Due date", self)
    self._due_date = QtGui.QLabel(self)

    task_info_layout.setWidget(0, QtGui.QFormLayout.LabelRole, task_name_lbl)
    task_info_layout.setWidget(0, QtGui.QFormLayout.FieldRole, self._task_name)
    task_info_layout.setWidget(1, QtGui.QFormLayout.LabelRole, project_lbl)
    task_info_layout.setWidget(1, QtGui.QFormLayout.FieldRole, self._project_name)
    task_info_layout.setWidget(2, QtGui.QFormLayout.LabelRole, shot_lbl)
    task_info_layout.setItem(2, QtGui.QFormLayout.FieldRole, shot_layout)
    task_info_layout.setWidget(3, QtGui.QFormLayout.LabelRole, shot_status_lbl)
    task_info_layout.setWidget(3, QtGui.QFormLayout.FieldRole, self._shot_status)
    task_info_layout.setWidget(4, QtGui.QFormLayout.LabelRole, task_status_lbl)
    task_info_layout.setWidget(4, QtGui.QFormLayout.FieldRole, self._task_status)
    task_info_layout.setWidget(5, QtGui.QFormLayout.LabelRole, due_date_lbl)
    task_info_layout.setWidget(5, QtGui.QFormLayout.FieldRole, self._due_date)
    task_frame_layout.addItem(task_info_layout)

    self._tab_widget = QtGui.QTabWidget(self)

    ## Display Nuke Assets from this task

    tab_asset_tree = QtGui.QWidget()
    tab_asset_tree_layout = QtGui.QVBoxLayout(tab_asset_tree)
    tab_asset_tree_layout.setContentsMargins(0,8,0,0)
    self.assets_widget = SceneAssetsWidget(self)
    tab_asset_tree_layout.addWidget(self.assets_widget)
    self._tab_widget.addTab(tab_asset_tree, "All Scene Assets")

    ## Display Notes from this task

    tab_notes = QtGui.QWidget()
    tab_notes_layout = QtGui.QVBoxLayout(tab_notes)
    tab_notes_layout.setContentsMargins(0,8,0,0)
    self._tab_widget.addTab(tab_notes, "Notes")

    task_frame_layout.addWidget(self._tab_widget)

  def _get_task_infos(self):
    if self._task == None:
      return
    self._t_project_name = self._task.getProject().getName()
    self._t_name = self._task.getName()
    
    if self._task.getParent() is not None:
      self._t_sequence_name = self._task.getParent().getName()

    if self._task.getParent() is not None:
      self._t_shot_name = self._task.getName()
      self._t_shot_status = self._task.getStatus()
    self._t_status = self._task.getStatus()
    try:
        self._t_due_date = self._task.getEndDate()
    except:
        self._t_due_date = None

  def initiate_task(self):
    if self._task == None:
      return

    self._project_name.setText(self._t_project_name)
    if self._t_sequence_name is not None:
      self._sequence_name.setText(self._t_sequence_name)
      self._sequence_name.setVisible(True)
      self._separator_shot.setVisible(True)
    else:
      self._sequence_name.setText("")
      self._sequence_name.setVisible(False)
      self._separator_shot.setVisible(False)

    if self._t_shot_name is not None:
      self._shot_name.setText(self._t_shot_name)
      self._shot_status.set_status(self._t_shot_status)
    else:
      self._shot_name.setText("None")
      self._shot_status.initiate()

    self._task_status.set_status(self._t_status)

    self._task_name.setText(self._t_name)
    end_date = self._t_due_date
    if end_date:
      self._due_date.setText(end_date.strftime("%Y-%m-%d"))
    else:
      self._due_date.setText("Unknown")

    self.assets_widget.initiate_task(self._task, self._current_scene)

  def set_read_only(self, bool_value):
    self._shot_status.set_read_only(bool_value)
    self._task_status.set_read_only(bool_value)

  def set_selection_mode(self, bool_value):
    self.assets_widget.set_selection_mode(bool_value)


from ftrack_connect_nuke.ftrackConnector.nukeassets import NukeSceneAsset

class SceneAssetsWidget(QtGui.QWidget):

  def __init__(self, parent=None):
    super(SceneAssetsWidget, self).__init__(parent)

    # self._scenes_connectors = SceneIO.connectors()

    self._connectors_per_type = dict()
    # for scene_connector in self._scenes_connectors:
    self._connectors_per_type['nuke_comp_scene'] = NukeSceneAsset()
    self._connectors_per_type['nuke_precomp_scene'] = NukeSceneAsset()
    self._connectors_per_type['nuke_roto_scene'] = NukeSceneAsset()


    self._task = None

    self.setupUI()

  def setupUI(self):
    css_settings_global = """
    QFrame { border: none; color: #FFF; }
    QCheckBox { color: #DDD; padding: 0px; background: none; }
    QComboBox { color: #DDD; padding: 2px; background: #333; }
    QComboBox::drop-down { border-radius: 0px; }
    QToolButton { color: #DDD; padding: 0px; background: #333; }
    """
    self.setStyleSheet(css_settings_global)

    main_layout = QtGui.QVBoxLayout(self)
    main_layout.setContentsMargins(0,0,0,0)
    main_layout.setSpacing(5)

    settings_frame = QtGui.QFrame(self)
    layout_settings = QtGui.QHBoxLayout(settings_frame)
    layout_settings.setContentsMargins(0,0,0,0)
    layout_settings.setSpacing(6)

    asset_types = [ "All Asset Types" ] + ['nuke_comp_scene', 'nuke_precomp_scene', 'nuke_roto_scene']

    self._asset_connectors_cbbox = QtGui.QComboBox(self)
    self._asset_connectors_cbbox.addItems(asset_types)
    self._asset_connectors_cbbox.currentIndexChanged.connect(self._update_tree)
    self._asset_connectors_cbbox.setMaximumHeight(23)
    self._asset_connectors_cbbox.setMinimumWidth(100)
    self._asset_connectors_cbbox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)

    self._refresh_btn = QtGui.QToolButton(self)
    self._refresh_btn.setText("refresh")
    self._refresh_btn.clicked.connect(self.initiate_assets_tree)

    spacer = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum )

    layout_settings.addWidget(self._asset_connectors_cbbox)
    layout_settings.addItem(spacer)
    layout_settings.addWidget(self._refresh_btn)
    main_layout.addWidget(settings_frame)

    self.assets_tree = AssetsTree(self)

    assets_colors = dict()
    # for connector_name, connector in self._connectors_per_type.iteritems():
    #   assets_colors[connector_name] = connector.color
    # self.assets_tree.add_assets_colors(assets_colors)

    main_layout.addWidget(self.assets_tree)

  def initiate_task(self, task, current_scene=None):
    self._task = task

    if current_scene != None:
      self._asset_connectors_cbbox.blockSignals(True)

      for i in range(1, self._asset_connectors_cbbox.count()):
        asset_type = self._asset_connectors_cbbox.itemText(i)
        connector = self._connectors_per_type[asset_type]
        if connector.asset_type == current_scene.connector.asset_type:
          self._asset_connectors_cbbox.setCurrentIndex(i)
          break

      self._asset_connectors_cbbox.blockSignals(False)

    self.initiate_assets_tree()

  def initiate_assets_tree(self):
    asset_types = [ self._asset_connectors_cbbox.currentText() ]
    if self._asset_connectors_cbbox.currentIndex() == 0:
      asset_types = None

    self.assets_tree.import_assets(self._task.getId(), asset_types)

  def _update_tree(self):
    asset_type = self._asset_connectors_cbbox.currentText()
    if self._asset_connectors_cbbox.currentIndex() == 0:
      asset_type = None
    self.assets_tree.update_display(asset_type)

  def set_selection_mode(self, bool_value):
    self.assets_tree.set_selection_mode(bool_value)
