#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError


class LutIO(AssetIO):
  ''' Describe a Lut asset
  '''

  @staticmethod
  def version_io():
    return LutVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import lut
    return [ lut.NukeLut() ]


class LutVersionIO(AssetVersionIO):
  ''' Describe a Lut asset version
  '''

  @staticmethod
  def asset_io():
    return LutIO
