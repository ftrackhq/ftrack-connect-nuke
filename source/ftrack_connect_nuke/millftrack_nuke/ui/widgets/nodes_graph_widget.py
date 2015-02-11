#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore

# import utilities

# from ...ftrack_io.asset import N_AssetFactory, AssetIOError
# from ...ftrack_io.assets.group_io import GroupIO

from ..images import image_dir

import os

from FnAssetAPI import logging
from ...controller import Controller


###############################################################################
# WIDGET
###############################################################################

class NodesGraphWidget(QtGui.QGraphicsView):
  nodes_loaded = QtCore.Signal()

  def __init__(self, parent=None):
    super(NodesGraphWidget, self).__init__(parent)

    self.size = QtCore.QSize(810,540)
    self.setupUI()

    self._nodes_cached = []
    self._assets_versions_dict = dict()
    self._groups = []

    self._is_loaded = False

  def setupUI(self):
    self.setMinimumSize(self.size)
    self.setMaximumSize(self.size)

    self.setStyleSheet("background: transparent; border: 0px; padding: 0px; margin: 0px;")

    self._edit_buttons = NodesGraphEditButtons(False, False, self)

    self._stackLayout_group = QtGui.QStackedLayout()

    layout = QtGui.QHBoxLayout(self)
    layout.setContentsMargins(0,0,0,0)
    layout.addLayout(self._stackLayout_group)

    self._loading_widget = QtGui.QFrame(self)
    self._loading_widget.setMinimumSize(self.size)
    self._loading_widget.setMaximumSize(self.size)
    loading_css = """
    QFrame{ border: 1px solid #444; border-radius: 4px;
            background: #333; padding: 3px; }
    """
    self._loading_widget.setStyleSheet(loading_css)
    layout_loading = QtGui.QHBoxLayout(self._loading_widget)
    label_loading = QtGui.QLabel("Nodes loading...", self._loading_widget)
    label_loading.setStyleSheet("border: 0px; background: none; color: #AAA")
    label_loading.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
    layout_loading.addWidget(label_loading)

    self._stackLayout_group.addWidget(self._loading_widget)

    self.nodes_viewer = NodesGraphView(self)
    self._stackLayout_group.addWidget(self.nodes_viewer)

    self._edit_buttons.zoom_level_toggled.connect(self.nodes_viewer.zoom_level)
    self._edit_buttons.handscroll_mode_toggled.connect(self.nodes_viewer.set_handscroll_mode)
    self._edit_buttons.drawing_mode_toggled.connect(self.nodes_viewer.set_painting_enable)
    self._edit_buttons.eraser_toggled.connect(self.nodes_viewer.erase_drawing)
    self._edit_buttons.color_modified.connect(self.nodes_viewer.set_pen_color)

  def import_nodes(self, nodes):
    self._stackLayout_group.setCurrentWidget(self._loading_widget)
    self._edit_buttons.update(False)

    # Thread that...
    self._controller = Controller(self._cache_nodes, args=(nodes,))
    self._controller.completed.connect(self.set_nodes)
    self._controller.start()

  def _cache_nodes(self, nodes):
    self._nodes_cached = []
    self._assets_versions_dict = dict()
    self._groups = []

    for node in nodes:
      if node.Class() in ["Backdrop", "Viewer"] :
        continue

      n = NodeCached(node)
      self._nodes_cached.append(n)

      if n.asset_version is not None:
        if n.asset_version.id not in self._assets_versions_dict.keys():
          self._assets_versions_dict[n.asset_version.id] = n

          if n.is_group:
            self._groups.append(n.asset_version)

  def set_nodes(self):
    self.nodes_viewer.import_nodes(self._nodes_cached)
    self._stackLayout_group.setCurrentWidget(self.nodes_viewer)

    self._edit_buttons.update(True)
    self._is_loaded = True

    self.nodes_loaded.emit()

  def save_thumbnail(self):
    pixmap = QtGui.QPixmap.grabWidget(self.nodes_viewer)
    # return utilities.get_pixmap_file( "Group_nodes", pixmap,
    #                                   overwrite=True )

  def is_loaded(self):
    return self._is_loaded

  def assets_versions_per_name(self):
    assets_versions_per_name = dict()
    for n in self._assets_versions_dict.values():
      if not n.is_group:
        assets_versions_per_name[n.name] = n.asset_version
    return assets_versions_per_name

  def clear_group_assets_versions(self):
    self._groups = []
    self.nodes_viewer.clear_highlight_group()

  def group_assets_versions(self):
    return self._groups


class NodeCached(object):
  def __init__(self, node):
    self.node = node
    self.name = node.name()

    self.xpos = node['xpos'].value()
    self.ypos = node['ypos'].value()

    self.max_inputs = node.maxInputs()
    self.max_outputs = node.maxOutputs()

    self.asset_version = None
    self.color = None
    self.color_linked_asset = None

    spherical_shape_classes = ["Camera2", "CameraXmlf", "Axis2", "AxisXmlf",
                            "TransformGeo", "Scene"]

    self.is_dot = (node.Class() == "Dot")
    self.is_spherical_shape = (node.Class() in spherical_shape_classes)

    self.is_group = False

    try:
      self.is_disabled = node['disable'].value()
    except:
      self.is_disabled = False

    if "ftrack_version_id" not in node.knobs().keys():
      return

    version_id = node.knobs()["ftrack_version_id"].value()

    try:
      self.asset_version = N_AssetFactory.get_version_from_id(version_id)
      self.color = QtGui.QColor()
      self.color.setNamedColor(self.asset_version.asset.connector.color)

      if self.asset_version.asset_io() == GroupIO:
        self.is_group = True

    except AssetIOError as err:
      logging.error(err)

    if self.is_group:
      try:
        previous_version_id = self.asset_version.linked_id(self.name)
        if previous_version_id is not None:
          previous_asset = N_AssetFactory.get_asset_from_version_id(previous_version_id)
          self.color_linked_asset = QtGui.QColor()
          self.color_linked_asset.setNamedColor(previous_asset.connector.color)

      except AssetIOError as err:
        logging.error(err)


class NodesGraphEditButtons(QtGui.QWidget):
  zoom_level_toggled = QtCore.Signal(int)
  handscroll_mode_toggled = QtCore.Signal(bool)
  drawing_mode_toggled = QtCore.Signal(bool)
  color_modified = QtCore.Signal(str)
  eraser_toggled = QtCore.Signal()

  def __init__(self, drawing_mode, handscroll_mode, parent=None):
    super(NodesGraphEditButtons, self).__init__(parent)

    self._drawing_mode = drawing_mode
    self._handscroll_mode = handscroll_mode

    self._icones = {
      'fitscreen' : os.path.join(image_dir, "fit_screen.png"),
      'fitscreen_ts' : os.path.join(image_dir, "fit_screen_trans.png"),
      'move' : os.path.join(image_dir, "handscroll.png"),
      'move_ts' : os.path.join(image_dir, "handscroll_trans.png"),
      'draw' : os.path.join(image_dir, "pencil.png"),
      'draw_ts' :os.path.join(image_dir, "pencil_trans.png"),
      'eraser' : os.path.join(image_dir, "eraser.png"),
      'eraser_ts' : os.path.join(image_dir, "eraser_trans.png"),
    }

    self.setupUI(parent)

  def setupUI(self, parent):
    button_css = """
      QToolButton{ background:rgba(255,255,255,50); border:none;
                   color: rgba(255,255,255,80); border-radius: 5px; }
      QToolButton:hover{ background:rgba(255,255,255,120);
                         color: rgba(255,255,255,200); }
      QToolButton:pressed{ background:rgba(255,255,255,80);
                           color: rgba(255,255,255,255); }
    """

    ## Colors buttons

    left_gap = 10
    self._color_white = QtGui.QToolButton(parent)
    self._color_white.setMaximumSize(QtCore.QSize(20,20))
    self._color_white.move(left_gap,parent.height()-30)
    self._color_white.clicked.connect( self._toggle_color )
    left_gap += self._color_white.width() + 10

    self._color_black = QtGui.QToolButton(parent)
    self._color_black.setMaximumSize(QtCore.QSize(20,20))
    self._color_black.move(left_gap,parent.height()-30)
    self._color_black.clicked.connect( self._toggle_color )
    left_gap += self._color_black.width() + 10

    self._color_red = QtGui.QToolButton(parent)
    self._color_red.setMaximumSize(QtCore.QSize(20,20))
    self._color_red.move(left_gap,parent.height()-30)
    self._color_red.clicked.connect( self._toggle_color )
    left_gap += self._color_red.width() + 10

    self._color_green = QtGui.QToolButton(parent)
    self._color_green.setMaximumSize(QtCore.QSize(20,20))
    self._color_green.move(left_gap,parent.height()-30)
    self._color_green.clicked.connect( self._toggle_color )
    left_gap += self._color_green.width() + 10

    self._color_blue = QtGui.QToolButton(parent)
    self._color_blue.setMaximumSize(QtCore.QSize(20,20))
    self._color_blue.move(left_gap,parent.height()-30)
    self._color_blue.clicked.connect( self._toggle_color )
    left_gap += self._color_blue.width() + 10

    self._color_yellow = QtGui.QToolButton(parent)
    self._color_yellow.setMaximumSize(QtCore.QSize(20,20))
    self._color_yellow.move(left_gap,parent.height()-30)
    self._color_yellow.clicked.connect( self._toggle_color )

    self._activate_color_button("white", False)
    self._activate_color_button("black", False)
    self._activate_color_button("red", True) # default
    self._activate_color_button("green", False)
    self._activate_color_button("blue", False)
    self._activate_color_button("yellow", False)

    ## Edit buttons

    left_gap = 10
    self._fit_screen = QtGui.QToolButton(parent)
    self._fit_screen.setMaximumSize(QtCore.QSize(20,20))
    self._fit_screen.setStyleSheet(button_css)
    self._fit_screen.move(left_gap,5)
    self._fit_screen.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    self._fit_screen.clicked.connect( self.fit_screen )
    self.activate_button(self._fit_screen, "fitscreen")
    left_gap += self._fit_screen.width() + 10

    self._zoom_out = QtGui.QToolButton(parent)
    self._zoom_out.setMaximumSize(QtCore.QSize(20,20))
    self._zoom_out.setStyleSheet(button_css)
    self._zoom_out.move(left_gap,5)
    self._zoom_out.setText("-")
    self._zoom_out.clicked.connect( self.zoom_out )
    left_gap += self._zoom_out.width() + 10

    self._zoom_in = QtGui.QToolButton(parent)
    self._zoom_in.setMaximumSize(QtCore.QSize(20,20))
    self._zoom_in.setStyleSheet(button_css)
    self._zoom_in.move(left_gap,5)
    self._zoom_in.setText("+")
    self._zoom_in.clicked.connect( self.zoom_in )
    left_gap += self._zoom_in.width() + 10

    self._drag = QtGui.QToolButton(parent)
    self._drag.setMaximumSize(QtCore.QSize(20,20))
    self._drag.move(left_gap,5)
    self._drag.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    self._drag.clicked.connect( self._toggle_handscroll_mode )
    self.set_handscroll_mode(self._handscroll_mode)
    left_gap += self._drag.width() + 10

    self._pencil = QtGui.QToolButton(parent)
    self._pencil.setMaximumSize(QtCore.QSize(20,20))
    self._pencil.move(left_gap,5)
    self._pencil.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    self._pencil.clicked.connect( self._toggle_drawing_mode )
    self.set_drawing_mode(self._drawing_mode)
    left_gap += self._pencil.width() + 10

    self._eraser = QtGui.QToolButton(parent)
    self._eraser.setMaximumSize(QtCore.QSize(20,20))
    self._eraser.move(left_gap,5)
    self._eraser.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
    self._eraser.clicked.connect( self._toggle_eraser )
    self.activate_button(self._eraser, "eraser", hover_emphasize=True)

  def _activate_color_button(self, color, bool_value):
    colors_button = dict(white=  self._color_white,
                         black=  self._color_black,
                         red=  self._color_red,
                         green=  self._color_green,
                         blue=  self._color_blue,
                         yellow=  self._color_yellow)

    btn_css = "background: %s; " % color
    if bool_value:
      btn_css += "border-radius: 5px; border: 3px solid rgb(200,200,200);"
      global_css = "QToolButton{%s}" % (btn_css)
      colors_button[color].setStyleSheet(global_css)
    else:
      btn_css += "border-radius: 5px; border: 3px solid rgb(100,100,100);"
      global_css = "QToolButton{%s}" % (btn_css)
      colors_button[color].setStyleSheet(global_css)
    colors_button[color].setIconSize(QtCore.QSize(18,18))

  def activate_button(self, button, icon_name=None, bool_value=False, hover_emphasize=False):
    if bool_value:
      if icon_name != None:
        btn_css = "background: url(%s) rgba(230,120,120,150); " % self._icones[icon_name]
      else:
        btn_css = "background: rgba(230,120,120,150); "
      btn_css += "border-radius: 5px; border: none;"
      global_css = "QToolButton{%s}" % (btn_css)
      button.setStyleSheet(global_css)

    else:
      if hover_emphasize:
        hover_background = "rgba(230,120,120,150)"
      else:
        hover_background = "rgba(255,255,255,80)"
      if icon_name != None:
        btn_css = "background: url(%s) rgba(255,255,255,50); " % self._icones[icon_name+"_ts"]
        btn_css += "border-radius: 5px; border: none;"
        btn_hover_css = "background: url(%s) %s;" % (self._icones[icon_name], hover_background)
      else:
        btn_css = "background: rgba(255,255,255,50); "
        btn_css += "border-radius: 5px; border: none;"
        btn_hover_css = "background: %s;" % hover_background
      global_css = "QToolButton{%s} QToolButton:hover{%s}" % (btn_css, btn_hover_css)
      button.setStyleSheet(global_css)
    button.setIconSize(QtCore.QSize(18,18))

  def set_drawing_mode(self, bool_value):
    if self._handscroll_mode and bool_value:
      self.set_handscroll_mode(False)
    self.activate_button(self._pencil, "draw", bool_value)
    self._drawing_mode = bool_value
    self.drawing_mode_toggled.emit(bool_value)
    self.raise_color_buttons(bool_value)

  def set_handscroll_mode(self, bool_value):
    if self._drawing_mode and bool_value:
      self.set_drawing_mode(False)
    self.activate_button(self._drag, "move", bool_value)
    self._handscroll_mode = bool_value
    self.handscroll_mode_toggled.emit(bool_value)

  def _toggle_drawing_mode(self):
    self.set_drawing_mode(not self._drawing_mode)

  def _toggle_handscroll_mode(self):
    self.set_handscroll_mode(not self._handscroll_mode)

  def _toggle_eraser(self):
    self.eraser_toggled.emit()

  def _toggle_color(self):
    colors = { self._color_white  : "white",
               self._color_black  : "black",
               self._color_red    : "red",
               self._color_green  : "green",
               self._color_blue   : "blue",
               self._color_yellow : "yellow" }
    self.set_color( colors[self.sender()] )

  def set_color(self, color_chosen):
    colors = ["white", "black", "red", "green", "blue", "yellow"]
    for color in colors:
      self._activate_color_button(color, color == color_chosen)
    self.color_modified.emit(color_chosen)

  def raise_color_buttons(self, bool_value):
    colors = [ self._color_white, self._color_black, self._color_red,
               self._color_green, self._color_blue, self._color_yellow ]
    for color in colors:
      color.setVisible(bool_value)
      color.raise_()

  def fit_screen(self):
    self.zoom_level_toggled.emit(0)

  def zoom_in(self):
    self.zoom_level_toggled.emit(1)

  def zoom_out(self):
    self.zoom_level_toggled.emit(-1)

  def update(self, display_edit_buttons):
    edit_buttons = [ self._zoom_in, self._zoom_out, self._drag,
                     self._pencil, self._eraser, self._fit_screen ]

    if display_edit_buttons:
      for button in edit_buttons:
        button.raise_()
        button.setVisible(True)
      self.set_drawing_mode(False)
      self.set_handscroll_mode(False)
    else:
      for button in edit_buttons:
        button.setVisible(False)


class NodesGraphView(QtGui.QGraphicsView):
  def __init__(self, parent=None):
    super(NodesGraphView, self).__init__(parent)

    self.setGeometry(QtCore.QRect(0,0,parent.width(),parent.height()))

    self._scale_factor = 1.15

    global_css = """
    QGraphicsView{ border: 1px solid #444; border-radius: 4px;
                   background: #333; padding: 3px; }
    """
    self.setStyleSheet(global_css)

    self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                         QtGui.QSizePolicy.Expanding))

    self._scene = QtGui.QGraphicsScene(parent)
    self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
    self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing)
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    self._nodes_dict = dict()
    self._drawings = []

    image_pen = os.path.join(image_dir,"pencil.png")
    image_pen_px = QtGui.QPixmap(image_pen)
    image_pen_px.setMask(image_pen_px.mask())
    self._image_pen_cursor = QtGui.QCursor(image_pen_px)

    self._pen_color = QtCore.Qt.red

    self._drawing_mode = False
    self._pencil_pressed = False
    self._position_mouse = None

    self.setScene(self._scene)

  @staticmethod
  def default_node_color():
    return QtGui.QColor(171, 171, 171)

  def import_nodes(self, nodes_cached):
    self._nodes_dict = dict()
    for node_cached in nodes_cached:
      if node_cached.is_dot:
        self._nodes_dict[node_cached.node] = DotItem(node_cached, self.scene())
      elif node_cached.is_spherical_shape:
        self._nodes_dict[node_cached.node] = CircleNodeItem(node_cached, self.scene())
      else:
        self._nodes_dict[node_cached.node] = NodeItem(node_cached, self.scene())

    for node_cached in nodes_cached:
      for input in node_cached.node.dependencies():
        if input in self._nodes_dict.keys():
          self.link(self._nodes_dict[input], self._nodes_dict[node_cached.node])

    self.center()

  def clear_highlight_group(self):
    for item in self._nodes_dict.values():
      if item.node_cached.is_group:
        if item.node_cached.color_linked_asset is not None:
          item.default_color = item.node_cached.color_linked_asset
        else:
          item.default_color = NodesGraphView.default_node_color()

  def zoom_level(self, level):
    if level > 0:
      self.scale(self._scale_factor, self._scale_factor)
    elif level < 0:
      self.scale(1.0/self._scale_factor, 1.0/self._scale_factor)
    elif level == 0:
      self.center()

  def center(self):
    rect = self.bounding_box_items()
    self.setSceneRect(rect)
    self.fitInView(rect, QtCore.Qt.KeepAspectRatio)

  def bounding_box_items(self):
    bounding_rect = None

    for item in self._nodes_dict.values() + self._drawings:
      rect = item.sceneBoundingRect()
      if bounding_rect == None:
        bounding_rect = rect
      else:
        bounding_rect = rect.united(bounding_rect)

    if bounding_rect is None:
      bounding_rect = QtCore.QRectF()

    adjust_width = 0
    adjust_height = 0

    if bounding_rect.width() < bounding_rect.height():
      width = self.geometry().width() * bounding_rect.height() / float(self.geometry().height())
      adjust_width = (width-bounding_rect.width()) * 0.5
    else:
      height = self.geometry().height() * bounding_rect.width() / float(self.geometry().width())
      adjust_height = (height-bounding_rect.height()) * 0.5

    bounding_rect = bounding_rect.adjusted( -adjust_width, -adjust_height,
                                            adjust_width, adjust_height )

    return bounding_rect

  def set_selectable_nodes(self, bool_value):
    for item in self._nodes_dict.values():
      item.set_selectable(bool_value)

  def set_handscroll_mode(self, bool_value):
    if bool_value:
      self.set_selectable_nodes(False)
      self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
    else:
      self.set_selectable_nodes(True)
      self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

  def set_painting_enable(self, bool_value):
    self._drawing_mode = bool_value
    if bool_value:
      self.set_selectable_nodes(False)
      self.viewport().setCursor(self._image_pen_cursor)
      self.setDragMode(QtGui.QGraphicsView.NoDrag)
    else:
      self.set_selectable_nodes(True)
      self.viewport().setCursor(QtCore.Qt.ArrowCursor)
      self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

  def set_pen_color(self, color):
    qt_colors = dict(white=  QtCore.Qt.white,
                     black=  QtCore.Qt.black,
                     red=  QtCore.Qt.red,
                     green=  QtCore.Qt.green,
                     blue=  QtCore.Qt.blue,
                     yellow=  QtCore.Qt.yellow)
    self._pen_color = qt_colors[color]

  def erase_drawing(self):
    for drawing in self._drawings:
      self._scene.removeItem(drawing)
    self._drawings = []

  def mousePressEvent(self, event):
    result = super(NodesGraphView, self).mousePressEvent(event)
    self._pencil_pressed = (self._drawing_mode == True)
    return result

  def mouseMoveEvent(self, event):
    result = super(NodesGraphView, self).mouseMoveEvent(event)
    if self._pencil_pressed:
      position = self.mapToScene( event.pos() )
      if self._position_mouse == None:
        self._position_mouse = position
      else:
        pen = QtGui.QPen()
        pen.setCosmetic(True)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setColor(self._pen_color)
        pen.setWidth(3)

        graphics_path = QtGui.QGraphicsLineItem()
        graphics_path.setPen(pen)
        graphics_path.setVisible(True)

        graphics_path.setLine( QtCore.QLineF( self._position_mouse, position ) )
        self._scene.addItem(graphics_path)
        self._drawings.append(graphics_path)
        self._position_mouse = position
    return result

  def mouseReleaseEvent(self, event):
    result = super(NodesGraphView, self).mouseReleaseEvent(event)
    self._pencil_pressed = False
    self._position_mouse = None
    return result

  def link(self, node1, node2):
    link = Link(node1, node2)
    link.track_nodes()
    self._scene.addItem(link)

  def wheelEvent(self, event):
    num_degrees = event.delta() / 8
    num_steps = num_degrees / 15

    self.zoom_level(num_steps)
    event.accept()


###############################################################################
# ITEMS
###############################################################################

class NodeItem(QtGui.QGraphicsItem):
  def __init__(self, node_cached, scene):
    super(NodeItem, self).__init__()
    self.node_cached = node_cached
    self._links = []
    self._text = self.node_cached.name

    self._font = QtGui.QFont()
    self._font.setPixelSize(12)
    self._font.setWeight(QtGui.QFont.Normal)

    self._size = QtCore.QSize(20,5)
    self._radius = 5

    self.default_color = NodesGraphView.default_node_color()
    if self.node_cached.color is not None:
      self.default_color = self.node_cached.color
    self._text_color = QtGui.QColor(34, 34, 34)
    self._IO_color = QtGui.QColor(132, 132, 132)

    self.is_disabled = self.node_cached.is_disabled

    self.set_selectable(True)

    self.setPos(QtCore.QPoint(self.node_cached.xpos, self.node_cached.ypos))
    scene.addItem(self)

  def set_selectable(self, bool_value):
    self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, bool_value)
    self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, bool_value)

  def add_link(self, link):
    self._links.append(link)

  def boundingRect(self):
    return self.outline_rect().adjusted(-5, -5, +5, +5)

  def outline_rect(self):
    global_rect = QtCore.QRectF(-self._size.width()/2.0, self._size.height()/2.0,
                                self._size.width(), self._size.height())
    metrics = QtGui.QFontMetricsF(self._font)
    rect = metrics.boundingRect(self._text)
    rect.adjust(-8, -8, 8, 8)
    rect.translate(-rect.center())
    return rect.united(global_rect)

  def input_pos(self):
    return QtCore.QPointF(self.pos().x(), self.pos().y() - self._size.height() / 2.0 - 10)

  def output_pos(self):
    return QtCore.QPointF(self.pos().x(), self.pos().y() + self._size.height() / 2.0 + 10)

  def shape(self):
    rect = self.outline_rect()
    path = QtGui.QPainterPath()
    path.addRoundRect(rect.adjusted(-1,-1,+1,+1), self._radius, self._radius)
    return path

  def paint(self, painter, option, widget):
    pen = QtGui.QPen(self._text_color)
    if option.state & QtGui.QStyle.State_Selected:
      pen.setStyle(QtCore.Qt.DotLine)
      pen.setWidth(2)

    rect = self.outline_rect()

    center_top = QtCore.QPointF(rect.topLeft().x() + rect.width()/2.0, rect.top())
    center_bottom = QtCore.QPointF(rect.bottomLeft().x() + rect.width()/2.0, rect.bottom())

    painter.setPen(pen)
    painter.setBrush(self._IO_color)

    if self.node_cached.max_inputs > 0:
      painter.drawEllipse(center_top, 5, 5 )
    if self.node_cached.max_outputs > 0:
      painter.drawEllipse(center_bottom, 5, 5 )

    if self.is_disabled:
      painter.setBrush(self._IO_color)
    else:
      painter.setBrush(self.default_color)

    painter.drawRoundRect(rect, self._radius, self._radius,
                          mode= QtCore.Qt.RelativeSize)

    painter.setPen(self._text_color)
    painter.setFont(self._font)
    painter.drawText(rect, QtCore.Qt.AlignCenter, self._text)

    if self.is_disabled:
      painter.setPen( QtGui.QPen(self._text_color, 2, QtCore.Qt.SolidLine) )
      painter.drawLine(rect.topLeft(), rect.bottomRight())
      painter.drawLine(rect.topRight(), rect.bottomLeft())

    for link in self._links:
      link.track_nodes()


class CircleNodeItem(NodeItem):
  def __init__(self, node_cached, scene):
    super(CircleNodeItem, self).__init__(node_cached, scene)
    self._radius = 35
    self.selection_point = 24.7487373415

  def input_pos(self):
    return self.pos()

  def output_pos(self):
    return self.pos()

  def boundingRect(self):
    margin = self._radius
    rect = QtCore.QRectF(-self._radius, -self._radius,
                         self._radius*2, self._radius*2)
    rect_text = self.outline_rect()
    return rect.united(rect_text)

  def shape(self):
    path = super(CircleNodeItem, self).shape()
    path.addEllipse(QtCore.QPointF(0,0), self._radius + 1, self._radius + 1)
    path.setFillRule(QtCore.Qt.WindingFill)
    return path

  def paint(self, painter, option, widget):
    pen = QtGui.QPen(self._text_color)
    if option.state & QtGui.QStyle.State_Selected:
      pen.setStyle(QtCore.Qt.DotLine)
      pen.setWidth(2)

    painter.setPen(pen)

    if self.is_disabled:
      painter.setBrush(self._IO_color)
    else:
      painter.setBrush(self.default_color)

    painter.drawEllipse(QtCore.QPointF(0,0), self._radius, self._radius)

    rect = self.outline_rect()

    painter.setPen(self._text_color)
    painter.setFont(self._font)
    painter.drawText(rect, QtCore.Qt.AlignCenter, self._text)

    if self.is_disabled:
      painter.setPen( QtGui.QPen(self._text_color, 2, QtCore.Qt.SolidLine) )
      painter.drawLine(QtCore.QPointF(-self.selection_point,self.selection_point),
                       QtCore.QPointF(self.selection_point,-self.selection_point))
      painter.drawLine(QtCore.QPointF(self.selection_point,self.selection_point),
                       QtCore.QPointF(-self.selection_point,-self.selection_point))

    for link in self._links:
      link.track_nodes()


class DotItem(CircleNodeItem):
  def __init__(self, node_cached, scene):
    super(DotItem, self).__init__(node_cached, scene)
    self._radius = 5

  def paint(self, painter, option, widget):
    pen = QtGui.QPen(self._text_color)
    if option.state & QtGui.QStyle.State_Selected:
      pen.setStyle(QtCore.Qt.DotLine)
      pen.setWidth(2)

    painter.setPen(pen)
    painter.setBrush(self._IO_color)
    painter.drawEllipse(QtCore.QPointF(0,0), self._radius, self._radius)

    for link in self._links:
      link.track_nodes()


class Link(QtGui.QGraphicsLineItem):
  def __init__(self, from_node, to_node):
    super(Link, self).__init__()
    self._from_node = from_node
    self._to_node = to_node

    self._from_node.add_link(self)
    self._to_node.add_link(self)

    self.setZValue(-1)

  def track_nodes(self):
    self.setLine(QtCore.QLineF(self._from_node.output_pos(),
                               self._to_node.input_pos()))

  def outline_rect(self):
    x1 = self._from_node.output_pos().x()
    y1 = self._from_node.output_pos().y()
    x2 = self._to_node.input_pos().x()
    y2 = self._to_node.input_pos().y()

    if x1 > x2:
      right_x = x1
      left_x = x2
    else:
      right_x = x2
      left_x = x1

    if y1 > y2:
      top_y = y2
      bottom_y = y1
    else:
      top_y = y1
      bottom_y = y2

    return QtCore.QRectF(QtCore.QPointF(left_x, top_y),
                         QtCore.QPointF(right_x, bottom_y))
