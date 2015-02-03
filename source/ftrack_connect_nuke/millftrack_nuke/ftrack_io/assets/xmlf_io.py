#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError


class XmlfIO(AssetIO):
  ''' Describe a xmlf asset
  '''

  @staticmethod
  def version_io():
    return XmlfVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import xmlf
    return [ xmlf.NukeXmlf() ]


class XmlfVersionIO(AssetVersionIO):
  ''' Describe a xmlf asset version
  '''

  @staticmethod
  def asset_io():
    return XmlfIO
