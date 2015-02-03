#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtCore

from logger import FT_logger


class WorkerSignal(QtCore.QObject):
  finished = QtCore.Signal(bool, str)

class Worker(QtCore.QRunnable):
  def __init__(self, callback, args, kwargs):
    super(Worker, self).__init__()
    self._callback = callback
    self._args = args
    self._kwargs = kwargs
    self.signal = WorkerSignal()

#  @FT_logger.profiler
  def run(self, *args):
    try:
      self._callback(*self._args, **self._kwargs)
    except Exception as err:
      FT_logger.debug(str(err), color="red")
      self.signal.finished.emit(False, str(err))
    else:
      self.signal.finished.emit(True, "")


class Controller(QtCore.QObject):
  completed = QtCore.Signal()
  error = QtCore.Signal(str)

  def __init__(self, func, args=None, kwargs=None):
    ''' initiate a new instance '''
    super(Controller, self).__init__()
    if args == None: args = ()
    if kwargs == None: kwargs = {}
    self.worker = Worker(func, args, kwargs)
    self.worker.signal.finished.connect(self._emit_signal)

  def _emit_signal(self, success, error_message):
    if success:
      self.completed.emit()
    else:
      self.error.emit(error_message)

  def start(self):
    QtCore.QThreadPool.globalInstance().start(self.worker)

