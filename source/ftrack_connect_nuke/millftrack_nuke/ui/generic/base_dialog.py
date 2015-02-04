#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftrack

from PySide import QtGui, QtCore


from ..widgets.message_widget import MessageWidget
from ..widgets.scope_widget import ScopeWidget
from ..images import image_dir

from ... import utilities

from ...controller import Controller

import os


class BaseDialog(QtGui.QDialog):
  '''
  Dialog Widget which should be used for every FTrack dialog. It contains an
  FTrack banner, the millftrack.user, the thumbnail and the possibility to add
  an extra command in the middle of the banner.

  The extra command is used in the script publisher panel.

  '''

  def __init__(self, parent=None):
    super(BaseDialog, self).__init__(parent)

    # self._user = MFTrackUser()
    self._user = ftrack.User(os.getenv('LOGNAME'))
    self._thumbnail_user = self._user.getThumbnail()

    self._error = False

    # Counter to insert header elements after the banner
    self._widget_header_count = 0

    self.setStyleSheet("QDialog{ background: #333; }")

    # Icon and title
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(os.path.join(image_dir, "mill_favicon.png")),
                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
    self.setWindowIcon(icon)

    self._main_layout = QtGui.QVBoxLayout(self)
    self._main_layout.setContentsMargins(0,0,0,0)
    self._main_layout.setSpacing(0)

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

    spacer_H1 = QtGui.QSpacerItem( 0, 0,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum )

    self._extra_cmd = ExtraCommand(self)
    self._extra_cmd.setVisible(False)

    spacer_H2 = QtGui.QSpacerItem( 0, 0,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum )

    self._username_lbl = QtGui.QLabel("You need to sign in...",self)
    self._username_lbl.setStyleSheet("QFrame{ background: none; }")
    self._avatar_frame = QtGui.QLabel(self)
    self._avatar_frame.setMinimumHeight(25)
    self._avatar_frame.setMaximumHeight(25)
    self._avatar_frame.setMinimumWidth(25)
    self._avatar_frame.setMaximumWidth(25)

    banner_layout.addWidget(logo_frame)
    banner_layout.addItem(spacer_H1)
    banner_layout.addWidget(self._extra_cmd)
    banner_layout.addItem(spacer_H2)
    banner_layout.addWidget(self._username_lbl)
    banner_layout.addWidget(self._avatar_frame)
    self._main_layout.addWidget(banner_frame)
    self._widget_header_count += 1

    self._error_box = MessageWidget(self)
    self._main_layout.addWidget(self._error_box)

    self._warning_box = MessageWidget(self)
    self._main_layout.addWidget(self._warning_box)

    # Body layout
    body_layout = QtGui.QVBoxLayout()
    body_layout.setContentsMargins(10,10,10,10)
    body_layout.setSpacing(6)

    # Contents layout
    self._global_content_layout = QtGui.QVBoxLayout()
    self._stackLayout = QtGui.QStackedLayout()
    self._global_content_layout.addLayout(self._stackLayout)

    self._content_widget = QtGui.QWidget(self)
    self._content_layout = QtGui.QVBoxLayout(self._content_widget)
    self._content_layout.setContentsMargins(0,0,0,0)
    self._content_layout.setSpacing(10)
    self._stackLayout.addWidget(self._content_widget)

    css_frame = """
    background:#222; border-radius: 4px;
    padding:10px; border: 0px;
    """

    self._loading_widget = QtGui.QWidget(self)
    self._loading_widget.setStyleSheet("background:#333")
    loading_layout = QtGui.QHBoxLayout(self._loading_widget)

    frame_loading = QtGui.QFrame(self)
    frame_loading.setMaximumSize(QtCore.QSize(250,200))
    frame_loading.setStyleSheet(css_frame)
    frame_loading.setFrameShape(QtGui.QFrame.StyledPanel)
    frame_loading.setFrameShadow(QtGui.QFrame.Raised)
    frame_loading_layout = QtGui.QVBoxLayout(frame_loading)

    loading_gif = os.path.join(image_dir, "mill_logo_light.gif")
    self.movie_loading = QtGui.QMovie(loading_gif, QtCore.QByteArray(), frame_loading)

    movie_screen_loading = QtGui.QLabel(frame_loading)
    movie_screen_loading.setSizePolicy( QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Expanding )
    movie_screen_loading.setAlignment(QtCore.Qt.AlignCenter)

    self._loading_lbl = QtGui.QLabel(frame_loading)
    self._loading_lbl.setText("Loading user tasks...")
    self._loading_lbl.setWordWrap(True)
    self._loading_lbl.setAlignment(QtCore.Qt.AlignCenter)

    frame_loading_layout.addWidget(movie_screen_loading)
    frame_loading_layout.addWidget(self._loading_lbl)

    loading_layout.addWidget(frame_loading)

    self.movie_loading.setCacheMode(QtGui.QMovie.CacheAll)
    self.movie_loading.setSpeed(100)
    movie_screen_loading.setMovie(self.movie_loading)

    self._stackLayout.addWidget(self._loading_widget)

    self._empty_widget = QtGui.QWidget(self)
    self._empty_widget.setStyleSheet("background:#333")
    empty_layout = QtGui.QHBoxLayout(self._empty_widget)

    frame_empty = QtGui.QFrame(self)
    frame_empty.setMaximumSize(QtCore.QSize(350,400))
    frame_empty.setStyleSheet(css_frame)
    frame_empty.setFrameShape(QtGui.QFrame.StyledPanel)
    frame_empty.setFrameShadow(QtGui.QFrame.Raised)
    frame_empty_layout = QtGui.QVBoxLayout(frame_empty)

    image = os.path.join(image_dir, "no_asset.png")
    css_image = """
    background: url(""" + image + """) no-repeat center center;
    """

    movie_screen_empty = QtGui.QFrame(frame_empty)
    movie_screen_empty.setMinimumSize(QtCore.QSize(300,300))
    movie_screen_empty.setStyleSheet(css_image)
    frame_empty_layout.addWidget(movie_screen_empty)
    empty_layout.addWidget(frame_empty)

    self._stackLayout.addWidget(self._empty_widget)

    self._stackLayout.setCurrentWidget(self._content_widget)

    body_layout.addItem(self._global_content_layout)

    # Dialog buttons
    # NOTE: We use "QPushButton" widgets because of a bug with the placement of
    # the "QDialogButtonBox" buttons with PySide
    layout_buttons = QtGui.QHBoxLayout()
    layout_buttons.setSpacing(10)
    spacer = QtGui.QSpacerItem( 40, 20,
                                QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Minimum )
    self._save_btn = QtGui.QPushButton("Save", self)
    self._cancel_btn = QtGui.QPushButton("Cancel", self)
    layout_buttons.addItem(spacer)
    layout_buttons.addWidget(self._cancel_btn)
    layout_buttons.addWidget(self._save_btn)
    body_layout.addItem(layout_buttons)

    self._main_layout.addItem(body_layout)

    self._save_btn.clicked.connect(self.accept)
    self._cancel_btn.clicked.connect(self.reject)

    self.set_user()

  def set_loading_mode(self, bool_value):
    if bool_value:
      self.movie_loading.start()
      self._stackLayout.setCurrentWidget(self._loading_widget)
    else:
      self._stackLayout.setCurrentWidget(self._content_widget)
      self.movie_loading.stop()
    self.set_enabled(not bool_value)

  def set_empty_task_mode(self, bool_value):
    self.movie_loading.stop()
    if bool_value:
      self._stackLayout.setCurrentWidget(self._empty_widget)
    else:
      self._stackLayout.setCurrentWidget(self._content_widget)
    self.set_enabled(not bool_value)

  @property
  def user_id(self):
    if self._user != None:
      return self._user.getId()

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

  def setFTrackTitle(self, title):
    super(BaseDialog, self).setWindowTitle("Mill FTrack - " + title)

  def set_enabled(self, bool_result):
    self._save_btn.setEnabled(bool_result)

  def addHeaderWidget(self, widget):
    self._main_layout.insertWidget(self._widget_header_count, widget)
    self._widget_header_count += 1

  def addContentWidget(self, widget):
    widget.setParent(self._content_widget)
    self._content_layout.addWidget(widget)

  def initiate_error_box(self):
    self._error_box.setVisible(False)
    self.set_enabled(True)
    self._error = False

  def initiate_warning_box(self):
    self._warning_box.setVisible(False)

  def is_error(self):
    return self._error

  def set_error(self, msg, detail=None):
    self._error_box.set_error(msg, detail)
    self.set_enabled(False)
    self._error = True

  def set_warning(self, msg, detail=None):
    self._warning_box.set_warning(msg, detail)

  def set_header_command(self, title, toggled_title, command):
    self._extra_cmd.set_title(title, toggled_title)
    self._extra_cmd.set_command(command)
    self._extra_cmd.setVisible(True)


class ExtraCommand(QtGui.QToolButton):
  '''
  Customed button which can be set on the middle of the banner.
  The extra command is used in the script publisher panel.

  '''
  def __init__(self, parent=None):
    super(ExtraCommand, self).__init__(parent)

    main_css = """
    QToolButton {background:transparent; border:none; color: #333;}
    QToolButton:hover {color: #888; text-decoration: underline;}
    """
    self.setStyleSheet(main_css)

    self._title = None
    self._title_toggled = None
    self._action = None

    self._toggled = False

    self.clicked.connect(self._toggle)

  def set_title(self, title, title_toggled=None):
    self._title = title
    if title_toggled == None:
      self._title_toggled = title
    else:
      self._title_toggled = title_toggled
    self.setText(self._title)

  def set_command(self, command):
    self._action = command

  def _toggle(self):
    if self._action == None:
      return
    self._action(self._toggled)
    self.setText(self._title if not self._toggled else self._title_toggled)
    self._toggled = not self._toggled


class BaseIODialog(BaseDialog):
  '''
  Dialog Widget which should be used whenever the content of the panel depends
  on a Task.

  '''

  def __init__(self, parent=None):
    super(BaseIODialog, self).__init__(parent)
    self._tasks_dict = dict()
    self._current_scene = None
    self._not_my_task = False
    self._display_tasks_list = True

    self._tasks_frame = QtGui.QFrame(self)
    self._tasks_frame.setStyleSheet("QFrame{background: #222; border:0px;}")
    self._tasks_frame.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                                QtGui.QSizePolicy.Maximum))

    self._header_layout = QtGui.QVBoxLayout(self._tasks_frame)
    self._header_layout.setContentsMargins(10,10,10,10)
    self._header_layout.setSpacing(8)

    mytask_layout = QtGui.QHBoxLayout()
    mytask_layout.setContentsMargins(0,0,0,0)
    mytask_layout.setSpacing(8)
    tasks_lbl = QtGui.QLabel("My tasks", self._tasks_frame)
    tasks_lbl.setMinimumWidth(60)
    tasks_lbl.setMaximumWidth(60)
    self._tasks_cbbx = QtGui.QComboBox(self._tasks_frame)
    self._tasks_cbbx.setMinimumHeight(23)
    self._tasks_cbbx.currentIndexChanged.connect(self.update_task_global)
    self._tasks_btn = QtGui.QPushButton("Browse all tasks...", self._tasks_frame)
    self._tasks_btn.setMinimumWidth(125)
    self._tasks_btn.setMaximumWidth(125)
    self._tasks_btn.clicked.connect(self.browse_all_tasks)

    mytask_layout.addWidget(tasks_lbl)
    mytask_layout.addWidget(self._tasks_cbbx)
    mytask_layout.addWidget(self._tasks_btn)

    self._header_layout.addItem(mytask_layout)
    self.addHeaderWidget(self._tasks_frame)

  def set_loading_mode(self, bool_value):
    super(BaseIODialog, self).set_loading_mode(bool_value)
    if self._display_tasks_list:
      self._tasks_frame.setVisible(not bool_value)

  def addHeaderTaskWidget(self, widget):
    self._header_layout.addWidget(widget)

  def addHeaderTaskItem(self, item):
    self._header_layout.addItem(item)

  def set_task(self, task):
    if task is None:
      return

    if task.parents in self._tasks_dict.keys():
      index = self._tasks_cbbx.findText( task.parents, QtCore.Qt.MatchFixedString )
      self._tasks_cbbx.setCurrentIndex(index)
    else:
      self._tasks_dict[task.parents] = task
      self._tasks_cbbx.insertItem(0,task.parents)
      self._tasks_cbbx.setCurrentIndex(0)

  def browse_all_tasks(self):
    from ..browser_dialog import BrowserDialog
    browser = BrowserDialog(self.current_task, self)
    if browser.result():
      self.set_task(browser.task)

  @property
  def current_task(self):
    if self._tasks_cbbx.currentText() != "":
      return self._tasks_dict[self._tasks_cbbx.currentText()]

  def initiate_tasks(self):
    self._tasks_dict = dict()

    self.set_loading_mode(True)

    # Thread that...
    self._controller = Controller(self._get_tasks)
    self._controller.completed.connect(self.set_tasks)
    self._controller.start()

  def _get_task_parents(self, task):
      parents = [t.getName() for t in task.getParents()]
      tasks = [t.getId() for t in task.getParents()]
      tasks.reverse()
      tasks.append(task.getId())
      parents.reverse()
      parents.append(task.getName())
      parents = ' / '.join(parents)
      return parents, tasks

  def _get_tasks(self):
    from ...ftrack_io.task import N_TaskFactory
    for task in N_TaskFactory.get_task_from_user(self._user):
      self._tasks_dict[task.parents] = task

    if self._current_scene != None:
      if self._current_scene.task.parents not in self._tasks_dict.keys():
        self._tasks_dict[self._current_scene.task.parents] = self._current_scene.task

  def set_tasks(self):
    self._tasks_cbbx.blockSignals(True)

    current_item_index = 0
    items = sorted(self._tasks_dict.keys())
    if self._current_scene != None:
      current_item_index = items.index(self._current_scene.task.parents)

    self._tasks_cbbx.addItems(items)
    self._tasks_cbbx.setCurrentIndex(current_item_index)

    self._tasks_cbbx.blockSignals(False)

    self.set_loading_mode(False)
    self.update_task_global()

  def display_tasks_frame(self, toggled):
    self._tasks_frame.setVisible(toggled)
    self._display_tasks_list = toggled

  def _validate_task(self):
    self.initiate_error_box()
    self.initiate_warning_box()

    ### Warning check

    warning = None
    if self.current_task != None:
      self._not_my_task = self._user.getId() not in self.current_task.users_ids
      if self._not_my_task:
        warning = "This task is not assigned to you. You might need to ask your \
supervisor to assign you to this task before publishing any asset.\n\
This action will be reported."

    if warning != None:
      self.set_warning(warning)

  def update_task_global(self):
    self.initiate_error_box()

    if self.current_task == None:
      error = "You don't have any task assigned to you."
      self.set_error(error)
      self.set_empty_task_mode(True)

    if not self.is_error():
      self.set_loading_mode(False)

    self.update_task()

  def update_task(self):
    raise NotImplementedError


class BaseIOScopeDialog(BaseIODialog):
  '''
  Dialog Widget which should be used whenever the content of the panel depends
  on a Task and when we need to access parent tasks (to load assets for example)

  '''
  def __init__(self, parent=None):
    super(BaseIOScopeDialog, self).__init__(parent)

    self._tasks_cbbx.currentIndexChanged.disconnect(self.update_task_global)
    self._tasks_cbbx.currentIndexChanged.connect(self.update_scope_widget)

    scope_layout = QtGui.QHBoxLayout()
    scope_layout.setContentsMargins(0,0,0,0)
    scope_layout.setSpacing(8)

    scope_lbl = QtGui.QLabel("Scope", self._tasks_frame)
    scope_lbl.setMinimumWidth(60)
    scope_lbl.setMaximumWidth(60)
    self._scope_widget = ScopeWidget(self._tasks_frame)
    self._scope_widget.clicked.connect(self.update_task_global)

    scope_layout.addWidget(scope_lbl)
    scope_layout.addWidget(self._scope_widget)

    self._header_layout.addItem(scope_layout)

  def set_tasks(self):
    self._tasks_cbbx.blockSignals(True)

    current_item_index = 0
    items = sorted(self._tasks_dict.keys())
    if self._current_scene != None:
      current_item_index = items.index(self._current_scene.task.parents)

    self._tasks_cbbx.addItems(items)
    self._tasks_cbbx.setCurrentIndex(current_item_index)

    self._tasks_cbbx.blockSignals(False)

    self.set_loading_mode(False)
    self.update_scope_widget()

  def update_scope_widget(self):
    if self._tasks_cbbx.currentText() != "":
      task = self._tasks_dict[self._tasks_cbbx.currentText()]
      self._scope_widget.initiate_task(task)

    self.update_task_global()

  @property
  def current_task(self):
    return self._scope_widget.current_task
