#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
import re
from FnAssetAPI import logging

from generic.base_dialog import BaseIODialog
from widgets.nodes_graph_widget import NodesGraphWidget
from widgets.message_widget import MessageWidget
from widgets.comment_widget import CommentWidget
from widgets.assets_tree import AssetsTree

# from ..ftrack_io.assets.group_io import GroupIO
# from ..ftrack_io.assets.scene_io import SceneIO

# from ..ftrack_io.asset import N_AssetFactory
# from ..ftrack_io.task import N_TaskFactory

# from ..ftrack_io.asset import AssetIOError


class GroupPublisherDialog(BaseIODialog):
  def __init__(self, nodes, version_id):
    logging.debug('version id: %s' % version_id)

    super(GroupPublisherDialog, self).__init__(QtGui.QApplication.activeWindow())
    self.setFTrackTitle("Publish a group of nodes...")

    self._nodes = nodes

    # self._group_connector = GroupIO.connectors()[0]

    # Dict used when several group assets are found in the nodes
    self._group_included_dict = dict()

    self.setupUI()

    # # Check current asset (None if no version_id found)
    # try:
    #   self._current_scene = N_AssetFactory.get_asset_from_version_id(version_id, SceneIO)
    # except AssetIOError as err:
    #   self.set_error(str(err))

    # self.initiate_tasks()

    self._nodes_graph.import_nodes(nodes)
    self._nodes_graph.nodes_loaded.connect(self._validate_group)

    self.exec_()

  def setupUI(self):
    self.resize(1410,950)
    self.setMinimumWidth(1410)
    self.setMinimumHeight(950)

    # GROUPS FOR TASK

    splitter = QtGui.QSplitter(self)
    splitter.setContentsMargins(0,0,0,10)
    splitter.setChildrenCollapsible(False)

    left_widget = QtGui.QWidget(splitter)
    left_widget.setMinimumWidth(570)
    left_layout = QtGui.QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0,0,5,0)

    css_task_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #252525; color: #FFF; }
    """
    css_label = "color: #c3cfa4; font-size: 12px; font-weight: bold;"

    task_frame = QtGui.QFrame(self)
    task_frame.setStyleSheet(css_task_global)
    task_frame_layout = QtGui.QVBoxLayout(task_frame)
    task_frame_layout.setContentsMargins(0,0,0,0)
    task_frame_layout.setSpacing(5)
    task_label = QtGui.QLabel("Groups available for this Task", task_frame)
    task_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    task_label.setStyleSheet(css_label)
    task_frame_layout.addWidget(task_label)
    self._group_tree = AssetsTree(self)
    # asset_colors = { self._group_connector.name : self._group_connector.color }
    # self._group_tree.add_assets_colors(asset_colors)
    self._group_tree.set_selection_mode(False)
    task_frame_layout.addWidget(self._group_tree)

    left_layout.addWidget(task_frame)
    splitter.addWidget(left_widget)

    # CONTENT GROUP

    right_widget = QtGui.QWidget(splitter)
    right_layout = QtGui.QVBoxLayout(right_widget)
    right_layout.setContentsMargins(5,0,0,0)

    css_asset_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #222; color: #FFF; font-size: 13px; }
    QLabel { padding: 0px; background: none; }
    """
    css_asset_name = """
    QLineEdit { padding: 3px; border-radius: 4px; border: 1px solid #444;
                background: #333; color: #FFF; font-weight: bold; }
    """
    css_asset_version = "color: #de8888; font-weight: bold;"

    asset_main_frame = QtGui.QFrame(self)
    asset_main_frame.setMinimumWidth(600)
    asset_main_frame.setStyleSheet(css_asset_global)
    asset_main_frame_layout = QtGui.QHBoxLayout(asset_main_frame)
    asset_main_frame_layout.setSpacing(10)
    asset_name_lbl = QtGui.QLabel("Asset", asset_main_frame)
    self._asset_name = QtGui.QLineEdit(asset_main_frame)
    self._asset_name.setText("Group_nodes")
    self._asset_name.textChanged.connect(self._validate_asset_name)
    self._asset_name.setStyleSheet(css_asset_name)
    asset_version_lbl = QtGui.QLabel("Version", asset_main_frame)
    self._asset_version = QtGui.QLabel("...", asset_main_frame)
    self._asset_version.setStyleSheet(css_asset_version)
    asset_main_frame_layout.addWidget(asset_name_lbl)
    asset_main_frame_layout.addWidget(self._asset_name)
    asset_main_frame_layout.addWidget(asset_version_lbl)
    asset_main_frame_layout.addWidget(self._asset_version)
    right_layout.addWidget(asset_main_frame)

    self._group_error_box = MessageWidget(right_widget)
    right_layout.addWidget(self._group_error_box)
    self._group_error_box._warning_header.setWordWrap(True)
    self._group_error_box._warning_header.setTextFormat(QtCore.Qt.RichText)

    self._group_warning_box = MessageWidget(right_widget)
    right_layout.addWidget(self._group_warning_box)
    self._group_warning_box._warning_header.setWordWrap(True)
    self._group_warning_box._warning_header.setTextFormat(QtCore.Qt.RichText)

    self._nodes_graph = NodesGraphWidget(right_widget)
    right_layout.addWidget(self._nodes_graph)

    self._comment_widget = CommentWidget(right_widget)
    self._comment_widget.changed.connect(self._validate_group)
    right_layout.addWidget(self._comment_widget)

    spacer = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Minimum,
                                      QtGui.QSizePolicy.Expanding )
    right_layout.addItem(spacer)

    splitter.addWidget(right_widget)

    self.addContentWidget(splitter)

    self._save_btn.setText("Publish Group of Nodes")
    self._save_btn.setMinimumWidth(170)
    self._save_btn.setEnabled(False)

  @property
  def comment(self):
    return self._comment_widget.text

  @property
  def asset_name(self):
    return self._asset_name.text()

  @property
  def asset_thumbnail(self):
    return self._nodes_graph.save_thumbnail()

  @property
  def nodes(self):
    return self._nodes

  @property
  def asset_version_nodes(self):
    return self._nodes_graph.assets_versions_per_name()

  def update_task(self):
    task = self.current_task
    self._save_btn.setEnabled(False)

    if task != None:
      self._group_tree.import_assets(task.group_assets)
      self._validate_asset_name()
      self._validate_group()

  def set_group_error(self, error=None, button=None, choices=None):
    if error != None:
      self._group_error_box.set_error(error, button=button, choices=choices)
    else:
      self._group_error_box.setVisible(False)
    self._save_btn.setEnabled(False)

  def set_group_warning(self, warning):
    self._group_warning_box.set_warning(warning)

  def initiate_group_error(self):
    self._group_error_box.setVisible(False)
    self._save_btn.setEnabled(True)

  def initiate_group_warning(self):
    self._group_warning_box.setVisible(False)

  def _validate_asset_name(self):
    self._asset_name.blockSignals(True)
    pattern_BadChar = re.compile("[^a-zA-Z0-9\._-]")
    asset_name = re.sub(pattern_BadChar, "", self._asset_name.text())
    self._asset_name.setText(asset_name)
    version = self.current_task.asset_version_number( asset_name,
                                                      self._group_connector.asset_type )
    self._asset_version.setText("%03d" % version)
    self._asset_name.blockSignals(False)

  def _version_the_included_group_asset(self, str_choice):
    if str_choice == "Yes I do":
      group_asset = self._nodes_graph.group_assets_versions()[0]
      if group_asset.asset.task != self.current_task:
        self.set_task(group_asset.asset.task)
      self._asset_name.setText(group_asset.name)

    self._nodes_graph.clear_group_assets_versions()
    self._validate_group()

  def _chose_which_group_to_version(self, group_name):
    for id_name, group_asset in self._group_included_dict.iteritems():
      if id_name == group_name:
        if group_asset.asset.task != self.current_task:
          self.set_task(group_asset.asset.task)
        self._asset_name.setText(group_asset.name)
        break

    self._nodes_graph.clear_group_assets_versions()
    self._validate_group()

  def _validate_group(self):
    if not self._nodes_graph.is_loaded():
      self._save_btn.setEnabled(False)
      return

    self._group_included_dict = dict()

    errors = []
    warnings = []

    choices = None
    button = None

    if len(self._nodes_graph.group_assets_versions()) == 1:
      group_asset = self._nodes_graph.group_assets_versions()[0]
      task_info = group_asset.asset.task.parents
      if group_asset.asset.task == self.current_task:
        task_info = "current task"
      error = "Some nodes already belong to this existing group asset:<br/>"
      error += "  - {0} [task: {1}]<br/>".format(group_asset.name, task_info)
      error += "<br/>Do you want to publish a version to this group?"

      choices = ["Yes I do", "No thanks"]
      button = ("Apply", self._version_the_included_group_asset)
      errors.append(error)

    elif len(self._nodes_graph.group_assets_versions()) > 1:
      error = "Some nodes already belong to one of these existing group assets:<br/>"
      choices = []
      for group_asset in self._nodes_graph.group_assets_versions():
        task_info = group_asset.asset.task.parents

        if group_asset.asset.task == self.current_task:
          task_info = "current task"
        error += " - {0} [task: {1}]<br/>".format(group_asset.name, task_info)

        group_name = group_asset.name
        i = 1
        while group_name in self._group_included_dict.keys():
          group_name = "{0} ({1})".format(group_asset.name, str(i))
          i += 1

        self._group_included_dict[group_name] = group_asset
        choices.append(group_name)

      error += "<br/>Do you want to publish a version to one of these groups?"

      choices.append("No thanks")
      button = ("Apply", self._chose_which_group_to_version)
      errors.append(error)

    elif len(self.comment) == 0:
      errors.append("You must comment before publishing")

    if len(errors) > 0:
      self.set_group_error("<br/><br/>".join(errors), button, choices)
    else:
      self.initiate_group_error()

    if len(warnings) > 0:
      self.set_group_warning("<br/><br/>".join(warnings))
    else:
      self.initiate_group_warning()
