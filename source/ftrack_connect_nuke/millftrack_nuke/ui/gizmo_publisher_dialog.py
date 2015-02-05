#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
import os, re

from FnAssetAPI import logging

from generic.base_dialog import BaseIODialog
from widgets.script_editor_widget import ScriptEditorWidget
from widgets.message_widget import MessageWidget
from widgets.comment_widget import CommentWidget
from widgets.assets_tree import AssetsTree

# from ..ftrack_io.assets.gizmo_io import GizmoIO
# from ..ftrack_io.assets.scene_io import SceneIO

# from ..ftrack_io.asset import N_AssetFactory
# from ..ftrack_io.task import N_TaskFactory

# from ..ftrack_io.asset import AssetIOError


class GizmoPublisherDialog(BaseIODialog):
  def __init__(self, version_id):
    logging.debug('version id: %s' % version_id)

    super(GizmoPublisherDialog, self).__init__(QtGui.QApplication.activeWindow())
    self.setFTrackTitle("Publish a gizmo...")

    self.setupUI()

    self.initiate_tasks()

    self.exec_()

  def setupUI(self):
    self.resize(1300,900)
    self.setMinimumWidth(1300)
    self.setMinimumHeight(900)

    # GIZMOS FOR TASK

    splitter = QtGui.QSplitter(self)
    splitter.setContentsMargins(0,0,0,10)
    splitter.setChildrenCollapsible(False)

    left_widget = QtGui.QWidget(splitter)
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
    task_label = QtGui.QLabel("Gizmos available for this Task", task_frame)
    task_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    task_label.setStyleSheet(css_label)
    task_frame_layout.addWidget(task_label)
    self._gizmo_tree = AssetsTree(self, False)

    self._gizmo_tree.set_selection_mode(False)
    task_frame_layout.addWidget(self._gizmo_tree)

    left_layout.addWidget(task_frame)
    splitter.addWidget(left_widget)

    # CONTENT GIZMO

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
    self._asset_name.setText("Gizmo")
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

    file_layout = QtGui.QVBoxLayout()
    file_layout.setContentsMargins(0,0,0,0)
    file_layout.setSpacing(8)
    browser_layout = QtGui.QHBoxLayout()
    browser_layout.setContentsMargins(0,0,0,0)
    browser_layout.setSpacing(8)

    browser_label = QtGui.QLabel("Gizmo file", right_widget)
    browser_edit_css = """
    QLineEdit { border-radius: 4px; border: 1px solid #666;
                background: #555; color: #000; }
    """
    self._browser_edit = QtGui.QLineEdit(right_widget)
    self._browser_edit.setStyleSheet(browser_edit_css)
    self._browser_edit.textChanged.connect(self.set_gizmo_file)
    completer = QtGui.QCompleter(right_widget)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    completer.setCompletionMode(QtGui.QCompleter.InlineCompletion)
    dir = QtGui.QDirModel(completer)
    dir.setFilter(QtCore.QDir.Dirs|QtCore.QDir.NoDot|QtCore.QDir.NoDotDot)
    completer.setModel(dir)
    self._browser_edit.setCompleter(completer)
    self._browser_btn = QtGui.QToolButton(right_widget)
    self._browser_btn.setText("...")
    self._browser_btn.clicked.connect(self._browse_gizmo)
    browser_layout.addWidget(browser_label)
    browser_layout.addWidget(self._browser_edit)
    browser_layout.addWidget(self._browser_btn)
    file_layout.addItem(browser_layout)

    self._file_error_box = MessageWidget(right_widget)
    file_layout.addWidget(self._file_error_box)
    self._file_error_box._warning_header.setWordWrap(True)
    self._file_error_box._warning_header.setTextFormat(QtCore.Qt.RichText)

    self._file_warning_box = MessageWidget(right_widget)
    file_layout.addWidget(self._file_warning_box)
    self._file_warning_box._warning_header.setWordWrap(True)
    self._file_warning_box._warning_header.setTextFormat(QtCore.Qt.RichText)

    self._gizmo_file_content = ScriptEditorWidget(right_widget)
    file_layout.addWidget(self._gizmo_file_content)
    self._gizmo_file_content.file_dropped.connect(self._initiate_dropped_file)
    right_layout.addItem(file_layout)

    self._comment_widget = CommentWidget(right_widget)
    self._comment_widget.changed.connect(self._validate_gizmo)
    right_layout.addWidget(self._comment_widget)

    splitter.addWidget(right_widget)

    self.addContentWidget(splitter)

    self._save_btn.setText("Publish Gizmo")
    self._save_btn.setMinimumWidth(150)
    self._save_btn.setEnabled(False)

  @property
  def comment(self):
    return self._comment_widget.text

  @property
  def asset_name(self):
    return self._asset_name.text()

  @property
  def gizmo_path(self):
    return self._browser_edit.text()

  def update_task(self):
    task = self.current_task
    self._save_btn.setEnabled(False)

    if task != None:
      self._gizmo_file_content.set_enabled(False)

      # self._gizmo_tree.import_assets(task.gizmo_assets)

      self._validate_asset_name()
      self._validate_gizmo()

  def _browse_gizmo(self):
    import nuke
    title = 'Please select a Gizmo file...'
    file = nuke.getFilename(title, default=self._browser_edit.text())
    if file != None:
      if os.path.isfile(file):
        self._browser_edit.blockSignals(True)
        self._browser_edit.setText(file)
        self._browser_edit.blockSignals(False)
        self.set_gizmo_file(file)

  def _initiate_dropped_file(self, file):
    self._browser_edit.blockSignals(True)
    self._browser_edit.setText(file)
    self._browser_edit.blockSignals(False)
    self.set_gizmo_file(file)

  def set_gizmo_file(self, file_path):
    self._asset_name.setText("Gizmo")
    self._asset_version.setText("...")

    self._gizmo_file_content.initiate()
    if file_path == "":
      self.set_gizmo_error()
      self.initiate_gizmo_warning()
      self._gizmo_file_content.set_enabled(False)
      return

    elif not os.path.isfile(file_path):
      error = "%s is not a file..." % file_path
      self.set_gizmo_error(error)
      self.initiate_gizmo_warning()
      return

    elif not os.access(file_path, os.R_OK):
      error = "Impossible to open the file %s" % file_path
      self.set_gizmo_error(error)
      self.initiate_gizmo_warning()
      return

    file_name = os.path.basename(file_path)
    if not file_name.endswith(".gizmo"):
      error = "This file '%s' is not a gizmo. It should have the extension '.gizmo'" % file_name
      self.set_gizmo_error(error)
      self.initiate_gizmo_warning()
      return

    try:
      self._gizmo_file_content.set_file(file_path)
      self._gizmo_file_content.set_enabled(True)
      asset_name = file_name.rsplit(".gizmo")[0]
      self._asset_name.setText(asset_name)

    except Exception as err:
      error = "Impossible to read the file %s [%s]" % (file_name, str(err))
      self.set_gizmo_error(error)
      self.initiate_gizmo_warning()
      return

    else:
      self._validate_gizmo()

  def set_gizmo_error(self, error=None):
    if error != None:
      self._file_error_box.set_error(error)
    else:
      self._file_error_box.setVisible(False)
    self._save_btn.setEnabled(False)

  def set_gizmo_warning(self, warning):
    self._file_warning_box.set_warning(warning)

  def initiate_gizmo_error(self):
    self._file_error_box.setVisible(False)
    self._save_btn.setEnabled(True)

  def initiate_gizmo_warning(self):
    self._file_warning_box.setVisible(False)

  def _validate_asset_name(self):
    self._asset_name.blockSignals(True)
    pattern_BadChar = re.compile("[^a-zA-Z0-9\._-]")
    asset_name = re.sub(pattern_BadChar, "", self._asset_name.text())
    self._asset_name.setText(asset_name)
    asset = self.current_task.getAssets(assetTypes=['nuke_gizmo'])
    version = 0

    if asset :
        asset = asset[0]        
        version = asset.getVersions()
        if version:
            version = version[-1].get('version')

    self._asset_version.setText("%03d" % version)
    self._asset_name.blockSignals(False)

  def _validate_gizmo(self):
    if self._gizmo_file_content.file == None:
      return
    self._gizmo_file_content.set_enabled(True)

    # validate gizmo...
    errors = []
    warnings = []

    path_pattern = re.compile("(?<=( |\"|\'))(/[a-zA-Z0-9\.\#_-]+/[a-zA-Z0-9\.\#_-]+)+")

    layers = []
    stacks_pushed = []
    stacks_set = []
    absolute_paths = []
    server_paths = []

    for gizmo_line in self._gizmo_file_content.script_lines:
      if gizmo_line.is_layer_addition():
        layers.append( gizmo_line.clean_line )
      elif gizmo_line.stack_pushed() != None:
        stacks_pushed.append( gizmo_line.stack_pushed() )
      elif gizmo_line.stack_set() != None:
        stacks_set.append( gizmo_line.stack_set() )
      elif not gizmo_line.is_comment():
        match_path = re.search(path_pattern, gizmo_line.clean_line)
        if match_path != None:
          if not match_path.group(0).startswith("/mill3d/server/"):
            path = match_path.group(0)
            absolute_paths.append( (path, gizmo_line.line_number) )
          else:
            path = match_path.group(0)
            server_paths.append( (path, gizmo_line.line_number) )

    for stack_pushed in sorted(stacks_pushed):
      if stack_pushed not in stacks_set:
        error = "The gizmo is incorrect, one variable pushed havn't \
been set [%s]" % stack_pushed
        errors.append(error)

    if len(absolute_paths) > 0:
      error = "You can't publish gizmos containing absolute paths:<br>"
      for path_tuple in absolute_paths:
        path, line_number = path_tuple
        error += " - %s [line %d]<br/>" % (path, line_number)
      errors.append(error)

    wrong_server_paths = []
    for path_tuple in server_paths:
      if not os.access(path_tuple[0], os.R_OK):
        wrong_server_paths.append(path_tuple)

    if len(wrong_server_paths) > 0:
      error = "Some server based files are incorrect:<br>"
      for path_tuple in server_paths:
        path, line_number = path_tuple
        error += " - %s [line %d]<br/>" % (path, line_number)
      error +="<br/>Please contact RnD."
      errors.append(error)

    if len(layers) != 0:
      warning = "<strong>This gizmo add %d layer(s) to your script.</strong><br/>\
This can interact with the layers already set in your script (The built-in layers \
or those set by certain inputs such as the EXR files). Please check carefully the \
validity of these layers before publishing the gizmos" % len(layers)
      warnings.append(warning)

    if len(errors) == 0 and len(self.comment) == 0:
      errors.append("You must comment before publishing")

    if len(errors) > 0:
      self.set_gizmo_error("<br/><br/>".join(errors))
    else:
      self.initiate_gizmo_error()

    if len(warnings) > 0:
      self.set_gizmo_warning("<br/><br/>".join(warnings))
    else:
      self.initiate_gizmo_warning()
