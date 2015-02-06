#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftrack
from PySide import QtGui, QtCore
import os

from generic.base_dialog import BaseDialog

from images import image_dir
from FnAssetAPI import logging

TYPE_DICT = {
  "e5139355-61da-4c8f-9db4-3abc870166bc" : "Sequence",
  "22139355-61da-4c8f-9db4-3abc870166bc" : "Episode",
  "ab77c654-df17-11e2-b2f3-20c9d0831e59" : "Build",
  "4be63b64-5010-42fb-bf1f-428af9d638f0" : "Asset",
  "bad911de-3bd6-47b9-8b46-3476e237cb36" : "Shot",
  "11c137c0-ee7e-4f9c-91c5-8c77cec22b2c" : "Task",
  "": "Project"
}



class BrowserDialog(BaseDialog):
  def __init__(self, task=None, parent=None):
    super(BrowserDialog, self).__init__(parent)
    self.setFTrackTitle("Browse to a task...")
    self.setupUI()

    self._projects_browsers = dict()
    self.set_projects()

    self._tasks_per_path = dict()

    if task != None:
      self.set_task(task)

    self.exec_()

  def setupUI(self):
    self.resize(1100,670)

    location_frame = QtGui.QFrame(self)
    location_frame.setStyleSheet("QFrame{background: #222; border:0px;}")
    location_layout = QtGui.QGridLayout(location_frame)
    location_layout.setContentsMargins(10,10,10,10)
    location_layout.setSpacing(6)
    location_lbl = QtGui.QLabel("Task", location_frame)
    location_lbl.setMaximumWidth(65)
    self._location_cbbx = QtGui.QComboBox(location_frame)
    self._location_cbbx.currentIndexChanged.connect(self.update_browser)
    location_layout.addWidget(location_lbl,0,0,1,1)
    location_layout.addWidget(self._location_cbbx,0,1,1,1)
    self.addHeaderWidget(location_frame)

    main_widget = QtGui.QWidget(self)
    main_layout = QtGui.QHBoxLayout(main_widget)
    main_layout.setSpacing(6)
    project_frame = QtGui.QFrame(self)
    project_frame.setMaximumWidth(340)
    css_project = """
    QFrame { padding: 3px; border-radius: 4px; background: #252525; }
    QLabel { padding: 0px; background: none; font-size: 13px; }
    """
    project_frame.setStyleSheet(css_project)
    projects_layout = QtGui.QVBoxLayout(project_frame)
    projects_lbl = QtGui.QLabel("PROJECTS", project_frame)
    projects_lbl.setMinimumHeight(30)
    projects_lbl.setAlignment(QtCore.Qt.AlignCenter)
    self._projects_list = TaskList(project_frame)
    projects_layout.addWidget(projects_lbl)
    projects_layout.addWidget(self._projects_list)
    main_layout.addWidget(project_frame)

    self._stackLayout = QtGui.QStackedLayout()
    content_widget = QtGui.QWidget(main_widget)
    layout_content = QtGui.QHBoxLayout(content_widget)
    layout_content.setContentsMargins(0,0,0,0)
    layout_content.addLayout(self._stackLayout)
    main_layout.addWidget(content_widget)

    self.addContentWidget(main_widget)

    self._save_btn.setText("Open")
    self.set_enabled(False)

  @property
  def task(self):
    if self._location_cbbx.currentText() in self._tasks_per_path.keys():
      return self._tasks_per_path[self._location_cbbx.currentText()]

  def set_projects(self):
    self._projects_list.add_items(ftrack.getProjects())
    self._projects_list.item_selected.connect(self.call_project_browser)

  def call_project_browser(self, current_project):
    if current_project.getId() not in self._projects_browsers.keys():
      widget = BrowserProject(current_project, self)
      widget.task_selected.connect(self.set_selected_task)
      self._stackLayout.addWidget(widget)
      self._projects_browsers[current_project.getId()] = widget
    self._stackLayout.setCurrentWidget(self._projects_browsers[current_project.getId()])

  def set_selected_task(self, task):
    parents = self._get_task_parents(task)
    self._location_cbbx.blockSignals(True)
    self._tasks_per_path[parents] = task
    self._location_cbbx.insertItem(0,parents)
    self._location_cbbx.setCurrentIndex(0)
    self._location_cbbx.blockSignals(False)
    self.set_enabled(True)

  def update_browser(self):
    task = self._tasks_per_path[self._location_cbbx.currentText()]
    self.set_task(task)

  def set_task(self, task):

    item = self._projects_list.findItems( task.getProject().getName(),
                                          QtCore.Qt.MatchFixedString )[0]
    self._projects_list.setCurrentItem(item)
    browser = self._stackLayout.currentWidget()
    block_signal = self.sender() != None # to avoid loops...
    browser.set_task(task, block_signal)


class BrowserProject(QtGui.QScrollArea):
  task_selected = QtCore.Signal(object)

  def __init__(self, project, parent=None):
    super(BrowserProject, self).__init__(parent)
    self.setupUI()

    self._widget_per_level = dict()
    self.add_task(project)

  def setupUI(self):
    css_scroll = """
    QScrollArea { padding: 3px; border: 0px; border-radius: 4px;
                  background: #252525; }
    QScrollBar { border: 0; border-radius: 6px;background-color: #333;
                 margin: 1px; }
    QScrollBar::handle { background: #222; border: 1px solid #111; }
    QScrollBar::sub-line, QScrollBar::add-line { height: 0px; width: 0px; }
    """
    self.setStyleSheet(css_scroll)
    self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
    self.setWidgetResizable(True)
    self._scrollAreaWidgetContents = QtGui.QWidget()
    self._scrollAreaWidgetContents.setStyleSheet("background: #252525;")
    main_layout = QtGui.QHBoxLayout(self._scrollAreaWidgetContents)
    self.setWidget(self._scrollAreaWidgetContents)

  def add_task(self, current_task, new_level=0):
    for level in self._widget_per_level.keys():
      if level >= new_level:
        self._widget_per_level[level].close()
        del self._widget_per_level[level]

    children = current_task.getChildren()
    tasks = current_task.getTasks()

    if len(children) > 0 or len(tasks) > 0:
      current_task_list = TaskList(self._scrollAreaWidgetContents, new_level)
      current_task_list.add_items(children, tasks)
      current_task_list.item_selected.connect(self.add_task)
      current_task_list.task_selected.connect(self._emit_task_selected)
      self._scrollAreaWidgetContents.layout().addWidget(current_task_list)
      self._widget_per_level[new_level] = current_task_list

  def _emit_task_selected(self, task):
    self.task_selected.emit(task)

  def set_task(self, task, block_signal):
    parents = task.getParents()
    parents = [p.getName() for p in parents]
    parents.reverse()
    parents.append(task.getName())
    path_list = parents[1:]  # Without the project

    for i in range(len(path_list)):
      browserlist = self._widget_per_level[i]
      if i == len(path_list) - 1 and block_signal:
        browserlist.blockSignals(True)

      item = browserlist.findItems(path_list[i], QtCore.Qt.MatchFixedString)[0]
      browserlist.setCurrentItem(item)

      if i == len(path_list) - 1 and block_signal:
        browserlist.blockSignals(False)


class TaskList(QtGui.QListWidget):
  item_selected = QtCore.Signal(object, int)
  task_selected = QtCore.Signal(object)

  def __init__(self, parent=None, level=0):
    super(TaskList, self).__init__(parent)
    self.setupUI()

    self._icones_per_type_name = {
      'Project' : os.path.join(image_dir, "project.png"),
      'Sequence' : os.path.join(image_dir, "sequence.png"),
      'Episode' : os.path.join(image_dir, "episode.png"),
      'Build' : os.path.join(image_dir, "build_group.png"),
      'Asset' : os.path.join(image_dir, "build.png"),
      'Shot' : os.path.join(image_dir, "shot.png"),
      'Task' : os.path.join(image_dir, "task.png")
    }

    self._level = level
    self._element_per_item = dict()
    self._tasks_per_item = dict()

  def setupUI(self):
    self.setMinimumWidth(200)

    self.setAlternatingRowColors(True)
    css_list = """
      QScrollBar { border: 0; border-radius: 6px; background-color: #333;
                   margin: 1px; }
      QScrollBar::handle { background: #222; border: 1px solid #111; }
      QScrollBar::sub-line, QScrollBar::add-line { height: 0px; width: 0px; }
      QListView { padding: 0px; border: 2px solid #222;
                  border-radius: 3px; background: #555; }
      QListView::item { height: 25px; }
      QListView::item { background: #666; }
      QListView::item:alternate { background: #555; }
      QListView::item:selected { background: orange; }
    """
    self.setStyleSheet(css_list)
    self.currentItemChanged.connect(self._emit_signals)

  def _emit_signals(self, current_item):
    new_level = self._level + 1
    if current_item.text() in self._element_per_item.keys():
      current_object = self._element_per_item[current_item.text()]
      self.item_selected.emit(current_object, new_level)
    elif current_item.text() in self._tasks_per_item.keys():
      current_task = self._tasks_per_item[current_item.text()]
      self.task_selected.emit(current_task)

  def add_items(self, list_children, list_tasks=None):
    self.clear()

    for child in list_children:
      self._element_per_item[child.getName()] = child
      item = QtGui.QListWidgetItem(child.getName(), self)
    
      # TODO: FIX ICONS FOR BROWSER 
      try:
        item_type_id = child.get('object_typeid')
      except:
        item_type_id = ''

      item_type = TYPE_DICT.get(item_type_id)

      if item_type in self._icones_per_type_name.keys():
        icon = QtGui.QIcon(self._icones_per_type_name[item_type])
        item.setIcon(icon)

      self.addItem(item)

    if list_tasks != None:
      for task in list_tasks:
        self._tasks_per_item[task.getName()] = task
      self.addItems(self._tasks_per_item.keys())
