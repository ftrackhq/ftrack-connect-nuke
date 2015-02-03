#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ftrack
from PySide import QtGui, QtCore
import os

from ..widgets.message_widget import MessageWidget
from ... import utilities

# from millftrack.user import MFTrackUser
from nukescripts import panels


class BaseDockableWidget(QtGui.QWidget):
  def __init__(self, parent=None):
    super(BaseDockableWidget, self).__init__(parent)

    self._name = None

    self._user = ftrack.User(os.getenv('LOGNAME'))
    self._thumbnail_user = self._user.getThumbnail()

    self._error = False

    self._main_layout = QtGui.QVBoxLayout(self)
    self._main_layout.setContentsMargins(0,0,0,0)
    self._main_layout.setSpacing(8)

    # Banner layout
    banner_frame = QtGui.QFrame(self)
    banner_frame.setStyleSheet("background: #000;")
    banner_layout = QtGui.QHBoxLayout(banner_frame)
    banner_layout.setContentsMargins(10,2,10,2)
    banner_layout.setSpacing(8)
    banner_frame.setMinimumHeight(40)
    banner_frame.setMaximumHeight(40)

    logo_frame = QtGui.QFrame(self)
    logo_frame.setMinimumHeight(30)
    logo_frame.setMaximumHeight(30)
    logo_frame.setMinimumWidth(180)
    logo_frame.setMaximumWidth(180)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo = os.path.join(current_dir,"..", "images", "banner.png")
    logo_frame.setStyleSheet("background: url(%s); border:0px;" % logo)

    spacer_H = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum )

    self._username_lbl = QtGui.QLabel("You need to sign in...",self)
    self._username_lbl.setStyleSheet("QFrame{ background: none; }")
    self._avatar_frame = QtGui.QLabel(self)
    self._avatar_frame.setMinimumHeight(25)
    self._avatar_frame.setMaximumHeight(25)
    self._avatar_frame.setMinimumWidth(25)
    self._avatar_frame.setMaximumWidth(25)

    banner_layout.addWidget(logo_frame)
    banner_layout.addItem(spacer_H)
    banner_layout.addWidget(self._username_lbl)
    banner_layout.addWidget(self._avatar_frame)
    self._main_layout.addWidget(banner_frame)

    self._error_box = MessageWidget(self)
    self._main_layout.addWidget(self._error_box)

    self._warning_box = MessageWidget(self)
    self._main_layout.addWidget(self._warning_box)

    self.set_user()

  def set_user(self):
    if self._user != None:
      self._username_lbl.setText( self._user.getName() )

    if not self._thumbnail_user:
      url = os.environ["FTRACK_SERVER"] + "/img/userplaceholder.png"
      self._thumbnail_user = url

    tempfile = utilities.get_url_file(self._thumbnail_user)
    imagePixmap = QtGui.QPixmap(tempfile)
    scaledPixmap = imagePixmap.scaled( 25,25, QtCore.Qt.KeepAspectRatio,
                                              QtCore.Qt.SmoothTransformation )
    self._avatar_frame.setPixmap(scaledPixmap)

  def initiate_error_box(self):
    self._error_box.setVisible(False)
    self._error = False

  def initiate_warning_box(self):
    self._warning_box.setVisible(False)

  def is_error(self):
    return self._error

  def set_error(self, msg, detail=None):
    self._error_box.set_error(msg, detail)
    self._error = True

  def set_error(self, msg, detail=None):
    self._error_box.set_error(msg, detail)
    self._error = True

  def set_warning(self, msg, detail=None):
    self._warning_box.set_warning(msg, detail)

  def addContentWidget(self, widget):
    self._main_layout.addWidget(widget)

  def addContentItem(self, item):
    self._main_layout.addLayout(item)

  def registerAsPanel(self, name, id):
    object_name = self.__class__.__name__
    return panels.registerWidgetAsPanel(object_name, name, id, create = True)