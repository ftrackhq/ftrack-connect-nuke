#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore

from generic.base_dialog import BaseIOScopeDialog
from widgets.assets_tree import AssetsTree
from images import image_dir

# from ..controller import Controller

# from ..ftrack_io.asset import N_AssetFactory
# from ..ftrack_io.task import N_TaskFactory

# from ..ftrack_io.asset import AssetIOError

# from ..ftrack_io.assets.scene_io import SceneIO

# from ..ftrack_io.assets.image_io import ImageIO
# from ..ftrack_io.assets.group_io import GroupIO
# from ..ftrack_io.assets.gizmo_io import GizmoIO
# from ..ftrack_io.assets.xmlf_io import XmlfIO
# from ..ftrack_io.assets.lut_io import LutIO

from FnAssetAPI import logging
import os


class AssetsLoaderDialog(BaseIOScopeDialog):

  def __init__(self, version_id):
    super(AssetsLoaderDialog, self).__init__(QtGui.QApplication.activeWindow())
    self.setFTrackTitle("Asset Management...")

    self._asset_types_order = [ (ImageIO, "Image Sequences"),
                                (GroupIO, "Group of Nodes"),
                                (GizmoIO, "Gizmos"),
                                (XmlfIO,  "Xmlf"),
                                (LutIO,   "Look-up Tables")  ]
    self._asset_types_btns = dict()

    self.setupUI()

    self._asset_trees_dict = dict()

    # Check current asset (None if no version_id found)
    try:
      self._current_scene = N_AssetFactory.get_asset_from_version_id(version_id, SceneIO)
    except AssetIOError as err:
      self.set_error(str(err))

    self.initiate_tasks()

  def setupUI(self):
    self.resize(100,900)
    self.setMinimumWidth(1000)
    self.setMinimumHeight(900)

    content_widget = QtGui.QWidget(self)
    main_layout = QtGui.QHBoxLayout(content_widget)
    main_layout.setContentsMargins(0,0,0,10)

    # FILTERS BUTTONS

    css_filter_type_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #252525; color: #FFF; }
    """
    css_label = "color: #c3cfa4; font-size: 12px; font-weight: bold;"

    filter_type_frame = QtGui.QFrame(content_widget)
    filter_type_frame.setStyleSheet(css_filter_type_global)
    filter_type_frame.setMaximumWidth(200)
    filter_type_frame_layout = QtGui.QVBoxLayout(filter_type_frame)
    filter_type_frame_layout.setContentsMargins(0,0,0,0)
    filter_type_frame_layout.setSpacing(5)
    types_label = QtGui.QLabel("Asset Types Filters", filter_type_frame)
    types_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    types_label.setStyleSheet(css_label)
    filter_type_frame_layout.addWidget(types_label)

    scroll_area = QtGui.QScrollArea(filter_type_frame)
    scroll_area.setWidgetResizable(True)
    scroll_area.setAlignment(QtCore.Qt.AlignCenter)
    scroll_area_content = QtGui.QWidget()
    scroll_area_content_layout = QtGui.QVBoxLayout(scroll_area_content)

    for asset_type, asset_name in self._asset_types_order:
      connector_name = asset_type.connectors()[0].name
      btn = AssetTypeButton(asset_name, scroll_area_content)
      self._asset_types_btns[connector_name] = btn
      self._asset_types_btns[connector_name].clicked.connect(self.update_assets)
      scroll_area_content_layout.addWidget(self._asset_types_btns[connector_name])

    spacer_btns = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Minimum,
                                           QtGui.QSizePolicy.Expanding )
    scroll_area_content_layout.addItem(spacer_btns)

    scroll_area.setWidget(scroll_area_content)
    filter_type_frame_layout.addWidget(scroll_area)

    main_layout.addWidget(filter_type_frame)

    # ASSET LIST

    asset_list_layout = QtGui.QVBoxLayout()
    asset_list_layout.setContentsMargins(10,0,0,0)
    asset_list_layout.setSpacing(10)

    arrow = os.path.join(image_dir, "branch-open.png")

    css_filter_name_global = """
    QFrame { padding: 3px; border-radius: 4px;
             background: #222; color: #FFF; font-size: 13px; }
    QLabel { padding: 0px; background: none; }
    """
    css_filter_edit = """
    QLineEdit { padding: 3px; border: 1px solid #444;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background: #333; color: #FFF; font-weight: bold; }
    """
    css_filter_cbbox = """
    QComboBox { padding: 2px 18px 2px 5px;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                background: #AAA; color: #333; }
    QComboBox::drop-down { subcontrol-origin: padding;
                           subcontrol-position: top right;
                           width: 15px; border: 0px;
                           border-top-right-radius: 0px;
                           border-bottom-right-radius: 0px; }
    QComboBox::down-arrow { image: url(""" + arrow + """) }
     """

    filter_sources = ["Asset Name", "Publisher", "Comment"]

    filter_name_frame = QtGui.QFrame(content_widget)
    filter_name_frame.setStyleSheet(css_filter_name_global)
    filter_name_frame_layout = QtGui.QHBoxLayout(filter_name_frame)
    filter_name_frame_layout.setSpacing(10)

    filter_name_label = QtGui.QLabel("Filter", filter_name_frame)
    filter_name_frame_layout.addWidget(filter_name_label)

    filter_name_role_layout = QtGui.QHBoxLayout()
    filter_name_role_layout.setContentsMargins(0,0,0,0)
    filter_name_role_layout.setSpacing(0)
    self._filter_cbbox = QtGui.QComboBox(filter_name_frame)
    self._filter_cbbox.addItems(filter_sources)
    self._filter_cbbox.currentIndexChanged.connect(self.update_assets)
    self._filter_cbbox.setMinimumWidth(80)
    self._filter_cbbox.setMinimumHeight(23)
    self._filter_cbbox.setStyleSheet(css_filter_cbbox)
    self._filter_name = QtGui.QLineEdit(filter_name_frame)
    self._filter_name.textEdited.connect(self.update_assets)
    self._filter_name.setStyleSheet(css_filter_edit)
    filter_name_role_layout.addWidget(self._filter_cbbox)
    filter_name_role_layout.addWidget(self._filter_name)
    filter_name_frame_layout.addItem(filter_name_role_layout)
    asset_list_layout.addWidget(filter_name_frame)

    self._stackLayout_tree = QtGui.QStackedLayout()
    self._tree_widget = QtGui.QWidget(content_widget)
    tree_layout = QtGui.QVBoxLayout(self._tree_widget)
    tree_layout.setContentsMargins(0,0,0,0)
    tree_layout.addLayout(self._stackLayout_tree)
    asset_list_layout.addWidget(self._tree_widget)

    main_layout.addItem(asset_list_layout)

    self.addContentWidget(content_widget)

    self._save_btn.setVisible(False)
    self._cancel_btn.setVisible(False)

    self.set_header_command( "Refresh tasks", None,
                             command=self._refresh_tasks )

  def _refresh_tasks(self, bool_value):
    self.initiate_tasks()

  def update_task(self):
    self.set_enabled(False)

    task = self.current_task
    if task is None:
      return

    if task.id not in self._asset_trees_dict.keys():
      asset_types = [t[0] for t in self._asset_types_order]
      widget = AssetTreeWidget(asset_types, self._tree_widget)
      widget.refresh_needed.connect(self.import_assets)
      widget.item_selected.connect(self._asset_is_selected)
      self._stackLayout_tree.addWidget(widget)
      self._asset_trees_dict[task.id] = widget

    else:
      asset_types = [k for k,v in self._asset_types_btns.iteritems() if v.selected]
      self._asset_trees_dict[task.id].update_display(asset_types, self._filter_name.text(),
                                                     self._filter_cbbox.currentText())

    self._asset_trees_dict[task.id].select_first_item()

    self._stackLayout_tree.setCurrentWidget(self._asset_trees_dict[task.id])
    self.import_assets()

  def import_assets(self):
    task = self.current_task
    if task is None:
      return

    asset_types = [t[0] for t in self._asset_types_order]
    assets = N_AssetFactory.get_assets_from_task(task.ftrack_object, asset_types)

    asset_types = [k for k,v in self._asset_types_btns.iteritems() if v.selected]
    widget = self._stackLayout_tree.currentWidget()

    widget.import_assets(assets, asset_types, self._filter_name.text())

  def update_assets(self):
    asset_types = [k for k,v in self._asset_types_btns.iteritems() if v.selected]
    widget = self._stackLayout_tree.currentWidget()
    widget.update_display( asset_types, self._filter_name.text(),
                           self._filter_cbbox.currentText() )

  def _asset_is_selected(self, asset_version):
    if asset_version is not None:
      if asset_version.is_available:
        self.set_enabled(True)


class AssetTypeButton(QtGui.QToolButton):

  def __init__(self, text, parent=None):
    super(AssetTypeButton, self).__init__(parent)
    self.setText(text)
    self.setMinimumHeight(80)
    self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.Fixed))

    self.selected = True
    self.set_style()

    self.clicked.connect(self._toggle_state)

  def set_selected(self, bool_value):
    self.selected(bool_value)
    self.set_style()

  def _toggle_state(self):
    self.selected = not self.selected
    self.set_style()

  def set_style(self):
    if self.selected:
      css = """
            background: #cbcbcb; color: #333;
            font-size: 13px; font-weight: bold;
            """
    else:
      css = """
            background: #252525; color: #FFF;
            font-size: 13px; font-weight: bold;
            """
    self.setStyleSheet(css)


class AssetTreeWidget(QtGui.QFrame):
  item_selected = QtCore.Signal(object)
  refresh_needed = QtCore.Signal()

  def __init__(self, assets_io, parent=None):
    super(AssetTreeWidget, self).__init__(parent)

    assets_colors = dict()
    for asset_io in assets_io:
      assets_colors[asset_io.connectors()[0].name] = asset_io.connectors()[0].color

    css_filter_tree = """
    QFrame { padding: 3px;
             border-top-right-radius: 0px;
             border-top-left-radius: 0px;
             border-bottom-right-radius: 4px;
             border-bottom-left-radius: 4px;
             background: #222; color: #FFF; }
    QLabel { padding: 0px; background: none; }
    """

    self.setStyleSheet(css_filter_tree)

    main_layout = QtGui.QVBoxLayout(self)

    self._assets_tree = AssetsTree(self)
    self._assets_tree.asset_version_selected.connect(self._emit_item_selected)
    self._assets_tree.set_draggable(True)
    self._assets_tree.add_assets_colors(assets_colors)
    main_layout.addWidget(self._assets_tree)

    layout_tools = QtGui.QHBoxLayout()
    self._refresh_btn = QtGui.QToolButton(self)
    self._refresh_btn.setText("refresh")
    self._refresh_btn.clicked.connect(self._refresh_tree)
    spacer = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Minimum )
    layout_tools.addItem(spacer)
    layout_tools.addWidget(self._refresh_btn)
    main_layout.addItem(layout_tools)

  @property
  def current_asset(self):
    return self._assets_tree.current_version

  def import_assets(self, assets, asset_types, filter):
    self._assets_tree.import_assets(assets, asset_types, filter)

  def update_display(self, asset_types, filter, filter_role):
    self._assets_tree.proxy_model.set_source(filter_role)
    self._assets_tree.update_display(asset_types, filter)

  def select_first_item(self):
    self._assets_tree.select_first_item()

  def _emit_item_selected(self, asset_version):
    self.item_selected.emit(asset_version)

  def _refresh_tree(self):
    self.refresh_needed.emit()
