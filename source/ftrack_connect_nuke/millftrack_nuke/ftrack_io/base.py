#!/usr/bin/env python
# -*- coding: utf-8 -*-


TYPE_DICT = {
  "e5139355-61da-4c8f-9db4-3abc870166bc" : "Sequence",
  "22139355-61da-4c8f-9db4-3abc870166bc" : "Episode",
  "ab77c654-df17-11e2-b2f3-20c9d0831e59" : "Build",
  "4be63b64-5010-42fb-bf1f-428af9d638f0" : "Asset",
  "bad911de-3bd6-47b9-8b46-3476e237cb36" : "Shot",
  "11c137c0-ee7e-4f9c-91c5-8c77cec22b2c" : "Task"
}


class FtrackObjectIO(object):
  def __init__(self, object):
    self.ftrack_object = object
    self.id = object.getId()
    try:
      self.name = object.getName()
    except: # AssetVersion has no getName() function...
      self.name = None

  @property
  def object_type(self):
    try:
      id_type = self.ftrack_object.get("object_typeid")
    except:
      return

    if id_type in TYPE_DICT.keys():
      return TYPE_DICT[id_type]

  @property
  def children(self):
    children_list = []
    for o in self.ftrack_object.getChildren():
      factory = FtrackObjectFactory()
      children_list.append(factory.get_object(o))
    return children_list

  @property
  def tasks(self):
    from task import N_TaskFactory
    tasks_list = []
    for t in self.ftrack_object.getTasks():
      tasks_list.append(N_TaskFactory.get_task(t))
    return tasks_list


class FtrackObjectFactory(object):

  ## Singleton instance
  _instance = None

  ## Object instances per task ID
  _objects_dict = dict()

  def __new__(cls):
    ''' Create a new instance '''
    if not cls._instance:
      cls._instance = super(cls.__class__, cls).__new__(cls)
    return cls._instance

  def __init__(self):
    ''' initiate a new instance '''
    pass

  def get_object(self, ftrack_object):
    if ftrack_object.getId() not in self._objects_dict.keys():
      self._objects_dict[ftrack_object.getId()] = FtrackObjectIO(ftrack_object)
    return self._objects_dict[ftrack_object.getId()]
