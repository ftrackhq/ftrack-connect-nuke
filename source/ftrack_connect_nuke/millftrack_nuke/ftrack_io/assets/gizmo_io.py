#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError


class GizmoIO(AssetIO):
  ''' Describe a Nuke Gizmo asset (file ending with ".gizmo")
  '''

  @staticmethod
  def version_io():
    return GizmoVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import gizmo
    return [ gizmo.NukeGizmo() ]


class GizmoVersionIO(AssetVersionIO):
  ''' Describe a Nuke Gizmo asset version
  '''

  @staticmethod
  def asset_io():
    return GizmoIO
