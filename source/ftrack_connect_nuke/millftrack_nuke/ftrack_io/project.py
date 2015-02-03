#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import FtrackObjectIO, FtrackObjectFactory

import ftrack


class ProjectIOError(Exception):
  pass


class ProjectIO(FtrackObjectIO):
  def __init__(self, project):
    super(ProjectIO, self).__init__(project)
    self.name = project.getFullName()


class ProjectFactory(FtrackObjectFactory):
  '''
  To avoid creating twice a ProjectIO from a ftrack Project object, we have a
  singleton Factory class which keep the IDs from the object converted.

  USAGE:
  from task import N_ProjectFactory
  task = N_ProjectFactory.get_project(task)

  '''

  ## Singleton instance
  _instance = None

  ## ProjectIO instances per task ID
  _projects_dict = dict()

  def __new__(cls):
    ''' Create a new instance '''
    if not cls._instance:
      cls._instance = super(cls.__class__, cls).__new__(cls)
    return cls._instance

  def __init__(self):
    ''' initiate a new instance '''
    pass

  def get_project(self, project):
    if project.getId() not in self._projects_dict.keys():
      self._projects_dict[project.getId()] = ProjectIO(project)
    return self._projects_dict[project.getId()]

  def get_project_from_task(self, task):
    return self.get_project(task.getProject())

  def get_all_projects(self):
    return [self.get_project(project) for project in ftrack.getProjects()]


## ProjectFactory singleton
N_ProjectFactory = ProjectFactory()
