#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

LOCATION = os.getenv('FTRACK_LOCATION_PLUGIN_PATH')
TOPIC = os.getenv('FTRACK_TOPIC_PLUGIN_PATH')

from assets_manager import AssetsManager
from FnAssetAPI import logging

import nuke
import ftrack_connect_nuke.millftrack_nuke

class MillFTrack(object):

  ## Singleton instance
  _instance = None

  def __new__(cls):
    ''' Create a new instance '''
    if not cls._instance:
      cls._instance = super(MillFTrack, cls).__new__(cls)
      logging.info('FTrack loaded.')
    return cls._instance

  def __init__(self):
    self._asset_manager = AssetsManager()

    self.initiate_preferences()
    self.initiate_callbacks()

  def setToUI(self):
    menubar = nuke.menu('Nuke')
    file_menu = menubar.menu('File')
    file_menu.addSeparator(index=1)
    file_menu.addCommand('FTrack - Open Script...', self._asset_manager.open_script_panel, index=2)
    file_menu.addCommand('FTrack - Publish Script...', self._asset_manager.publish_script_panel, index=3)
    self._asset_manager.recent_assets.menu = file_menu.addMenu('FTrack - Recent Scripts', index=4)
    file_menu.addSeparator(index=5)

    ftrack_menu = menubar.addMenu('&FTrack')
    ftrack_menu.addCommand('Assets Manager...', self._asset_manager.management_panel)
    ftrack_menu.addSeparator()
    ftrack_menu.addCommand('Publish a gizmo...', self._asset_manager.publish_gizmo_panel)
    ftrack_menu.addCommand('Publish a group of nodes...', self._asset_manager.publish_group_panel)
    ftrack_menu.addSeparator()
    ftrack_menu.addCommand('Manage the current Task', self.task_manager)
    ftrack_menu.addCommand('Manage the current Scene', self.scene_manager)

    from millftrack_nuke.ui.task_widgets import TaskManagerWidget
    from millftrack_nuke.ui.scene_widgets import SceneManagerWidget
    from nukescripts import panels

    # self._task_manager = TaskManagerWidget().registerAsPanel('FTrack Task Manager', "mill.TaskManagerWidget")
    # self._scene_manager = SceneManagerWidget().registerAsPanel('FTrack Scene Manager', "mill.TaskManagerWidget")

    widget_task = ''

    self._task_manager = panels.registerWidgetAsPanel(
        'millftrack_nuke.ui.task_widgets.TaskManagerWidget', 
        'FTrack Task Manager',
        id = "mill.TaskManagerWidget",
        create = True 
    )

    self._scene_manager = panels.registerWidgetAsPanel( 
        "millftrack_nuke.ui.scene_widgets.SceneManagerWidget", 
        'FTrack Scene Manager',
        id = "mill.SceneManagerWidget",
        create = True 
    )

    # Update Recent asset scenes menu...
    self._asset_manager.recent_assets.update_menu()

    # Check if an asset is already locked
    self._asset_manager.asset_locker.check_locked_scenes()

  def initiate_preferences(self):
    preferences = nuke.toNode('preferences')
    try:
      preferences["ftrack_preferences"]

    except:
      tab = nuke.Tab_Knob("ftrack_preferences", "Ftrack")
      tab.setFlag(nuke.ALWAYS_SAVE)
      preferences.addKnob(tab)

      debug_mode = nuke.Boolean_Knob("ftrack_debug_mode", "Debug Mode")
      debug_mode.setFlag(nuke.ALWAYS_SAVE)
      debug_mode.setFlag(nuke.STARTLINE)
      preferences.addKnob(debug_mode)

      profiling_mode = nuke.Boolean_Knob("ftrack_profiling_mode", "Profiling Mode")
      profiling_mode.setFlag(nuke.ALWAYS_SAVE)
      profiling_mode.setFlag(nuke.STARTLINE)
      preferences.addKnob(profiling_mode)

      log_folder_default = os.path.join(os.sep, "tmp", "ftrack")
      if not os.path.isdir(log_folder_default):
        os.mkdir(log_folder_default)

      log_folder = nuke.File_Knob("ftrack_log_folder", "Log Folder")
      log_folder.setFlag(nuke.ALWAYS_SAVE)
      log_folder.setFlag(nuke.STARTLINE)
      log_folder.setValue(log_folder_default)
      preferences.addKnob(log_folder)

  def initiate_callbacks(self):
    # Update script metadatas and links
    nuke.addOnScriptSave( self._asset_manager.update_script )

    # Update the lock parameter
    # TODO: deal with unlocked asset when Nuke crashes...
    nuke.addOnScriptLoad( self._asset_manager.lock_scene_asset )
    nuke.addOnScriptClose( self._asset_manager.unlock_scene_asset )

    # Load gizmos available
    nuke.addOnScriptLoad( AssetsManager.set_gizmos_to_toolbar )
    nuke.addOnScriptSave( AssetsManager.set_gizmos_to_toolbar )

    # Set drop callback
    import nukescripts
    nukescripts.addDropDataCallback(self._asset_manager.drop_asset_to_dag)

  def task_manager(self):
    pane = nuke.getPaneFor('Properties.1')
    self._task_manager.addToPane(pane)

  def scene_manager(self):
    pane = nuke.getPaneFor('Properties.1')
    self._scene_manager.addToPane(pane)


if nuke.env["gui"]:
    N_MillFTrack = MillFTrack()
