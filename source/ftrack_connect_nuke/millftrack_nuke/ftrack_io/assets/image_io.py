#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError


class ImageIO(AssetIO):
  ''' Describe an image asset
  '''

  @staticmethod
  def version_io():
    return ImageVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import image
    return [ image.ImageSequence() ]


class ImageVersionIO(AssetVersionIO):
  ''' Describe an image asset version
  '''

  @staticmethod
  def asset_io():
    return ImageIO
