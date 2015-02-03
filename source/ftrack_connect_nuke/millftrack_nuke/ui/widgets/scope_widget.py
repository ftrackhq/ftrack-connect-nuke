#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore

from FnAssetAPI import logging
from ...ftrack_io.task import N_TaskFactory


class ScopeWidget(QtGui.QWidget):
  clicked = QtCore.Signal()

  def __init__(self, parent=None):
    super(ScopeWidget, self).__init__(parent)
    self.setMinimumHeight(23)

    self._main_layout = QtGui.QVBoxLayout(self)
    self._main_layout.setContentsMargins(0,0,0,0)

    self._tasks_dict = dict()

    self._stackLayout = QtGui.QStackedLayout()
    self._main_layout.addLayout(self._stackLayout)

  def initiate_task(self, task):
    if task.id not in self._tasks_dict.keys():
      widget = ScopeSingleWidget(self, task)
      widget.clicked.connect(self._emit_clicked)
      self._stackLayout.addWidget(widget)
      self._tasks_dict[task.id] = widget

    widget = self._tasks_dict[task.id]
    self._stackLayout.setCurrentWidget(widget)

  def _emit_clicked(self):
    self.clicked.emit()

  @property
  def current_task(self):
    widget = self._stackLayout.currentWidget()
    try:
      return widget.btn_selected.task
    except:
      return

class ScopeSingleWidget(QtGui.QWidget):
  clicked = QtCore.Signal()

  def __init__(self, parent, task):
    super(ScopeSingleWidget, self).__init__(parent)

    self._main_layout = QtGui.QHBoxLayout(self)
    self._main_layout.setContentsMargins(0,0,0,0)
    self._main_layout.setSpacing(8)

    self._btns = []

    self._add_button("Shot: %s" % task.shot.name, task.shot)
    for parent_task in task.parent_tasks:
      self._add_button(parent_task.name, parent_task)
    self._add_button(task.name, task)

    self._btns[-1].set_activated(True)
    self.btn_selected = self._btns[-1]

    spacer = QtGui.QSpacerItem( 0, 0, QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum )
    self._main_layout.addItem(spacer)

  def _add_button(self, alias, task):
    btn_task = ScopeButton(self, alias, task)
    btn_task.activated.connect(self._change_activation)
    self._main_layout.addWidget(btn_task)
    self._btns.append(btn_task)

  def _change_activation(self):
    for btn in self._btns:
      if btn == self.sender():
        self.btn_selected = btn
        continue
      btn.set_activated(False)
    self.clicked.emit()


class ScopeButton(QtGui.QToolButton):
  activated = QtCore.Signal()

  def __init__(self, parent, alias, task):
    super(ScopeButton, self).__init__(parent)
    self.setText(alias)

    self.task = task
    self._activated = False

    self.clicked.connect(self._toggle_activation)
    self.initiate_style()

  def set_activated(self, bool_value):
    self._activated = bool_value
    self.initiate_style()

  def initiate_style(self):
    if self._activated:
      css_btn = "background: #FFF; color: #333; padding: 3px; border: 0px; border-radius: 3px;"
    else:
      css_btn = "background:transparent; color: #FFF; padding: 3px;"
    self.setStyleSheet(css_btn)

  def _toggle_activation(self):
    if not self._activated:
      self._activated = True
      self.initiate_style()
      self.activated.emit()

