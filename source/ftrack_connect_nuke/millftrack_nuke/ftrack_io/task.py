#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftrack import Task
from ftrack import FTrackError
from ftrack import getTaskStatuses, getShotStatuses

from base import FtrackObjectIO, FtrackObjectFactory
from project import N_ProjectFactory

from ..logger import FT_logger


class TaskIOError(Exception):
  pass


class TaskIO(FtrackObjectIO):

  @FT_logger.profiler
  def __init__(self, task):
    super(TaskIO, self).__init__(task)
    self.project = N_ProjectFactory.get_project_from_task(task)

    self._tokens_path = self._get_tokens(task)
    self.parents_list = [t.getName() for t in self._tokens_path]
    self.parents = " / ".join(self.parents_list)

    # Remove the current path from the tokens path to avoid loops
    self._tokens_path = self._tokens_path[:-1]

    self._tasks_only = [t for t in self._tokens_path if type(t) == Task]
    self._tasks_only.reverse()

    self._shot_object = None
    self._sequence_object = None

    self._shot_object = self._get_level(["Asset Build", "Shot"])

    if self._shot_object != None:
      if self._shot_object.getObjectType() != "Asset Build":
        self._sequence_object = self._get_level(["Sequence"])

    self.status = task.getStatus()
    try:
      self.end_date = task.getEndDate()
    except: # Shots don't have end date...
      self.end_date = None

  def _validate_path_name(self, tokens_path):
    return "_".join([t.getName().replace(" ","_") for t in tokens_path][:-1])

  def _get_tokens(self, task):
    task_list = [ task ]
    while hasattr(task, "getParent"):
      task = task.getParent()
      task_list = [ task ] + task_list
    return task_list

  def _get_level(self, level_type):
    for i in range(len(self._tasks_only)):
      task = self._tasks_only[i]
      if task.getObjectType() in level_type:
        self._tasks_only = self._tasks_only[i+1:]
        return task

  @property
  def parent_tasks(self):
    if self.shot == None:
      return

    parent_tasks = []

    for parent_task in sorted(self._tokens_path, reverse=True):
      if parent_task == self.shot.ftrack_object:
        break
      if type(parent_task) == Task:
        parent_tasks = [ N_TaskFactory.get_task(parent_task) ] + parent_tasks

    return parent_tasks

  @property
  def shot(self):
    if self._shot_object == None:
      return
    return N_TaskFactory.get_task(self._shot_object)

  @property
  def sequence(self):
    if self._sequence_object == None:
      return
    return N_TaskFactory.get_task(self._sequence_object)

  @property
  def web_widget_infos_Url(self):
    return self.ftrack_object.getWebWidgetUrl(name="info")

  @property
  def users_ids(self):
    return [user.getId() for user in self.ftrack_object.getUsers()]

  @property
  def scene_assets(self):
    from asset import N_AssetFactory
    from assets.scene_io import SceneIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [SceneIO])

  @property
  def read_assets(self):
    from asset import N_AssetFactory
    from assets.read_io import ReadIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [ReadIO])

  @property
  def group_assets(self):
    from asset import N_AssetFactory
    from assets.group_io import GroupIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [GroupIO])

  @property
  def gizmo_assets(self):
    from asset import N_AssetFactory
    from assets.gizmo_io import GizmoIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [GizmoIO])

  @property
  def xmlf_assets(self):
    from asset import N_AssetFactory
    from assets.xmlf_io import XmlfIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [XmlfIO])

  @property
  def lut_assets(self):
    from asset import N_AssetFactory
    from assets.lut_io import LutIO
    return N_AssetFactory.get_assets_from_task(self.ftrack_object, [LutIO])

  @property
  def users_ids(self):
    return [user.getId() for user in self.ftrack_object.getUsers()]

  def asset_version_number(self, asset_name, asset_type):
    from millftrack.cache import CachedAsset
    try:
      asset = self.ftrack_object.getAsset(asset_name, assetType=asset_type)
      asset_versions = CachedAsset.getVersions(asset)
      current_version = int(asset_versions[-1].getVersion()) + 1
    except FTrackError: # If asset doesn't exist
      current_version = 1
    return current_version

  @staticmethod
  def getTaskStatuses():
    return getTaskStatuses()

  @staticmethod
  def getShotStatuses():
    return getShotStatuses()


class TaskFactory(FtrackObjectFactory):
  '''
  To avoid creating twice a TaskIO from a ftrack Task object, we have a
  singleton Factory class which keep the IDs from the object converted.

  USAGE:
  from task import N_TaskFactory
  task = N_TaskFactory.get_task(task)

  '''

  ## TaskIO instance per task ID
  _tasks_dict = dict()

  def get_task(self, task):
    if task.getId() not in self._tasks_dict.keys():
      self._tasks_dict[task.getId()] = TaskIO(task)
    return self._tasks_dict[task.getId()]

  def get_task_from_asset(self, asset):
    task = Task(asset.get("taskid"))
    return self.get_task(task)

  def get_task_from_user(self, user):
    return [self.get_task(task) for task in user.tasks]


## TaskFactory singleton
N_TaskFactory = TaskFactory()