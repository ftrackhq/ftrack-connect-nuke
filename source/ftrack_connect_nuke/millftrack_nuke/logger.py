#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers

import os, time, inspect, getpass

import nuke


COLORS = dict(black=  '\033[0;30m',
              grey=   '\033[0;37m',
              white=  '\033[1;37m',
              blue=   '\033[0;34m',
              red=    '\033[0;31m',
              green=  '\033[0;32m',
              yellow= '\033[0;33m')


class FTFormatter(logging.Formatter):
  def __init__(self, fmt="%(levelno)s: %(msg)s"):
    logging.Formatter.__init__(self, fmt)
    self.end_C = '\033[0m'
    self.color_msg = None

  def _main_color(self, level):
    if self.color_msg in COLORS.keys():
      color = COLORS[self.color_msg]
    elif level == logging.DEBUG:
      color = COLORS["yellow"]
    elif level == logging.WARNING:
      color = COLORS["yellow"]
    elif level in [logging.ERROR, logging.CRITICAL]:
      color = COLORS["red"]
    else:
      color = COLORS["white"]
    return color

  def format(self, record):
    format_orig = self._fmt

    if record.levelno == logging.DEBUG:
      self._fmt = "{color1}[%(name)s]{endc} DEBUG: \
{color2}%(message)s{endc}".format( color1= COLORS["white"],
                                   color2= self._main_color(record.levelno),
                                   endc= self.end_C )

    elif record.levelno == logging.WARNING:
      self._fmt = "{color1}[%(name)s]{endc} WARNING: \
{color2}%(message)s{endc}".format( color1= COLORS["grey"],
                                   color2= self._main_color(record.levelno),
                                   endc= self.end_C )

    elif record.levelno == logging.INFO:
      self._fmt = "{color1}[%(name)s]{endc} \
{color2}%(message)s{endc}".format( color1= COLORS["grey"],
                                   color2= self._main_color(record.levelno),
                                   endc= self.end_C )

    elif record.levelno in [logging.ERROR, logging.CRITICAL]:
      self._fmt = "{color1}[%(name)s]{endc} %(levelname)s: \
{color2}%(message)s{endc}".format( color1= COLORS["white"],
                                   color2= self._main_color(record.levelno),
                                   endc= self.end_C )

    result = logging.Formatter.format(self, record)
    self._fmt = format_orig
    self.color_msg = None
    return result


class FTLogger(logging.Logger):

  ## Singleton instance
  _instance = None

  def __new__(cls):
    ''' Create a new instance '''
    if not cls._instance:
      cls._instance = super(FTLogger, cls).__new__(cls)
    return cls._instance

  def __init__(self):
    logging.Logger.__init__(self, 'Ftrack')
    self._log_filename = 'nuke_ftrack_{0}_log'.format(getpass.getuser())
    self._formatter_file = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    nuke.addKnobChanged(self.update_preferences, nodeClass="Preferences")

    nuke.nuke.addOnCreate(self.update_level, nodeClass="Preferences")
    nuke.nuke.addOnCreate(self.update_log_folder, nodeClass="Preferences")
    nuke.nuke.addOnCreate(self.update_profiler, nodeClass="Preferences")

    # formatters
    self._formatter_stdout = FTFormatter()

    # handlers
    self._streamer_handler = logging.StreamHandler()
    self._streamer_handler.setFormatter(self._formatter_stdout)
    self._rotater_handler = None

    self.addHandler(self._streamer_handler)

    # Profiling
    self._profiling = False
    self._profiling_calls = dict()

  def update_preferences(self):
    if nuke.thisKnob().name() == "ftrack_debug_mode":
      level = logging.DEBUG if bool(nuke.thisKnob().value()) else logging.INFO
      self.setLevel(level)
    elif nuke.thisKnob().name() == "ftrack_log_folder":
      log_path = nuke.thisKnob().value()
      self.set_log_folder(log_path)
    elif nuke.thisKnob().name() == "ftrack_profiling_mode":
      self._profiling = bool(nuke.thisKnob().value())

  def update_log_folder(self):
    preferences = nuke.toNode('preferences')
    try:
      log_path = preferences["ftrack_log_folder"].value()
      self.set_log_folder(log_path)
    except:
      self.set_log_folder(None)

  def update_level(self):
    preferences = nuke.toNode('preferences')
    try:
      debug = bool(preferences["ftrack_debug_mode"].value())
      self.setLevel( logging.DEBUG if debug else logging.INFO )
    except:
      self.setLevel( logging.INFO )

  def update_profiler(self):
    preferences = nuke.toNode('preferences')
    try:
      self._profiling = bool(preferences["ftrack_profiling_mode"].value())
    except:
      self._profiling = False

  def set_log_folder(self, log_path):
    success = False
    if log_path is not None:
      if os.path.isdir(log_path) and os.access(log_path, os.W_OK):
#        self.info("Log folder: {0}".format(str(log_path)))
        log_file = os.path.join(log_path, self._log_filename)
        self._rotater_handler = logging.handlers.RotatingFileHandler(
                                log_file, maxBytes=16000000, # 2MB
                                backupCount=10 )
        self._rotater_handler.setFormatter(self._formatter_file)
        self.addHandler(self._rotater_handler)
        success = True

    if not success:
      if self._rotater_handler is not None:
        self.removeHandler(self._rotater_handler)
      self.error("Impossible to set the log folder [{0}]".format(str(log_path)))

  def setLevel(self, level):
    self._streamer_handler.setLevel(level)
    if self._rotater_handler is not None:
      self._rotater_handler.setLevel(level)
    logging.Logger.setLevel(self, level)

  def debug(self, msg=None, color=None):
    back = inspect.currentframe().f_back
    frame = inspect.getframeinfo(back)

    try:
      info = '.'.join([back.f_locals['self'].__class__.__name__, frame.function])
    except KeyError:
      info = frame.function

    if msg is not None:
      msg = ' - '.join([info, str(msg)])
    else:
      msg = info

    self._formatter_stdout.color_msg = color
    logging.Logger.debug(self, msg)

  def info(self, msg=None, color=None):
    self._formatter_stdout.color_msg = color
    logging.Logger.info(self, msg)

  def profiler(self, f):
    def f_timer(*args, **kwargs):
      if not self._profiling:
        return f(*args, **kwargs)

      try:
        fc = '.'.join([args[0].__class__.__name__, f.__name__])
      except:
        fc = f.__name__

      if fc not in self._profiling_calls.keys():
        self._profiling_calls[fc] = 0
      self._profiling_calls[fc] += 1

      start = time.time()
      result = f(*args, **kwargs)
      end = time.time()

      msg = "Profile {0}: [call {1}] took {2} seconds".format(fc, str(self._profiling_calls[fc]),
                                                              str(end-start))
      self.info(msg, "green")

      return result
    return f_timer

## FTLogger singleton
FT_logger = FTLogger()
