#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftrack import Asset, AssetVersion, AssetType, User, Location
from ftrack import FTrackError

from base import FtrackObjectIO, FtrackObjectFactory
from task import N_TaskFactory

import os
from pytz import timezone

from FnAssetAPI import logging

from .. import utilities


class AssetIOError(Exception):
  pass


class AssetIO(FtrackObjectIO):
  '''Base Asset class'''

  def __init__(self, asset):
    super(AssetIO, self).__init__(asset)
    self.connector = self._get_connector()

  @staticmethod
  def connectors():
    raise NotImplemented

  @staticmethod
  def version_io(self):
    raise NotImplemented

  @property
  def task(self):
    return N_TaskFactory.get_task_from_asset(self.ftrack_object)

  @property
  def date_last_modif(self):
    return self.versions[-1].getDate()

  @property
  def versions(self):
    # TODO: Make this faster....
    from millftrack.cache import CachedAsset
    asset_versions = CachedAsset.getVersions(self.ftrack_object)
    return sorted(asset_versions, key=lambda v: v.getVersion())

  def _get_connector(self):
    connector = None
    connectors = self.connectors()
    ftrack_scene_asset_type = self.ftrack_object.getType()

    for scene_connector in connectors:
      if scene_connector.asset_type == ftrack_scene_asset_type.getShort():
        connector = scene_connector
        break

    if connector is None:
      error= "The object {0} has the wrong asset type to be cast as a scene [{1}].\
It should be one of these: {2}.".format(self.id, ftrack_scene_asset_type.getShort(),
                                        str([c.asset_type for c in connectors]))
      raise AssetIOError(error)

    return connector

  def lock_asset(self, bool_value):
    # TODO: give hostname information
    if bool_value:
      self.connector.lockAsset(self.ftrack_object)
    else:
      self.connector.unlockAsset(self.ftrack_object)

  @property
  def locker(self):
    user = self.connector.isLockedAsset(self.ftrack_object)
    if user == '':
      return

    try:
      ftrack_user = User(user)
    except FTrackError:
      self.lock_asset(False)
      return

    return ftrack_user


class AssetVersionIO(FtrackObjectIO):
  '''Base Asset Version class'''

  def __init__(self, asset_version):
    super(AssetVersionIO, self).__init__(asset_version)
    self._asset_version = asset_version

    from millftrack.cache import VersionDataCache
    from millftrack.objwrapper import VersionData

    # Cached Data
    vd = VersionDataCache(self._asset_version)
    self._version_data = vd.getData(regen=False)
    self._to_regen = not isinstance(self._version_data, VersionData)

    self.regen_image_cache = False

    # This parameter need to exist even if the cache is being regenerated
    self.version_number = self._asset_version.getVersion()
    self.name = self.asset.name

    if not self._to_regen:
      self.thumbnail = self._version_data.icon_url
      self.date = utilities.date_with_tz(self._version_data.date)
      self.status = self._version_data.status
      self.owner = asset_version.getUser()
      self.comment = asset_version.getComment()
      self.locations = self._version_data.avail

    else:
      self.thumbnail = None
      self.date = None
      self.status = None
      self.owner = None
      self.comment = None
      self.locations = None

  @staticmethod
  def asset_io():
    raise NotImplemented

  @staticmethod
  def default_thumbnail():
    thumnbail_ftrack_url = os.environ["FTRACK_SERVER"] + "/img/thumbnail2.png"
    return utilities.get_url_file(thumnbail_ftrack_url)

  @property
  def thumbnail_file(self):
    if self.thumbnail is None:
      return AssetVersionIO.default_thumbnail()
    file = utilities.get_url_file(self.thumbnail, self.regen_image_cache)
    self.regen_image_cache = False
    return file

  @property
  def asset(self):
    return N_AssetFactory.get_asset(self.ftrack_object.getAsset(), self.asset_io())

  @property
  def date_str(self):
    if self.date == None:
      return
    return self.date.strftime("%A, %d. %B %Y %I:%M%p")

  @property
  def is_being_cached(self):
    return self._to_regen

  @property
  def is_available(self):
    if self._to_regen:
      return False
    return utilities.MY_LOCATION in self.locations

  def regen_cache(self):
    from millftrack.cache import VersionDataCache
    vd = VersionDataCache(self._asset_version)
    self._version_data = vd.getData(regen=True)

    self.thumbnail = self._version_data.icon_url
    self.date = utilities.date_with_tz(self._version_data.date)
    self.status = self._version_data.status
    self.owner = self._asset_version.getUser()
    self.comment = self._asset_version.getComment()
    self.locations = self._version_data.avail

    self._to_regen = False

  @property
  def previous_version(self):
    if self.version_number == 0: return
    versions = self.asset.versions
    versions.reverse()
    for version in versions:
      if version.getVersion() < self.version_number:
        return N_AssetFactory.get_version(version, self.asset_io())

  @property
  def next_version(self):
    for version in self.asset.versions:
      if version.getVersion() > self.version_number:
        return N_AssetFactory.get_version(version, self.asset_io())

  def path(self, location_name=None, location_team=None):
    if not self.is_available:
      error = "This asset is not available in your location."
      raise AssetIOError(error)

    try:
      from millftrack.utilities import Component
      compo = self.ftrack_object.getComponents()[0]
      return Component.getPath(compo, location_name, location_team)
    except:
      error = "This asset doesn't have any component associated."
      raise AssetIOError(error)

  def load_dependencies(self):
    from assets.gizmo_io import GizmoIO
    import nuke

    for ftrack_version in self.ftrack_object.usesVersions():
      try:
        version = N_AssetFactory.get_version(ftrack_version)
        if version.asset_io() == GizmoIO:
          nuke.pluginAddPath(os.path.dirname(version.path()))
        version.load_dependencies()

      except AssetIOError as err:
        logging.error("Can't load some dependencies [{0}]".format(err))

  def load_asset(self):
    self.asset.connector.loadVersion(self.ftrack_object)

  def editor(self):
    return None


class AssetFactory(FtrackObjectFactory):
  '''
  To avoid creating twice a AssetIO or a AssetVersionIO from a ftrack object,
  we have a singleton Factory class which keep the IDs from the object converted.

  USAGE:
  from asset import AssetFactory
  from assets.scene_io import SceneIO
  scene = N_AssetFactory.get_asset(asset, SceneIO)

  '''

  _assets_dict = dict()
  _asset_versions_dict = dict()

  def _guess_asset_class(self, asset):
    import assets
    asset_class = None
    asset_type = asset.getType().getShort()

    for asset_class_instance in assets.all_assets():
      if asset_class is not None:
        break

      for connector in asset_class_instance.connectors():
        if connector.asset_type == asset_type:
          asset_class = asset_class_instance
          break

    if asset_class is None:
      error = "Impossible to guess the assetIO class of this Ftrack asset...[{0}]".format(asset.getId())
      raise AssetIOError(error)

    return asset_class

  def get_asset(self, asset, asset_class=None):
    # Try to guess the asset class if this has not been indicated
    if asset_class is None:
      asset_class = self._guess_asset_class(asset)

    if asset.getId() not in self._assets_dict.keys():
      self._assets_dict[asset.getId()] = asset_class(asset)
    return self._assets_dict[asset.getId()]

  def get_version(self, asset_version, asset_class=None):
    # Try to guess the asset class if this has not been indicated
    if asset_class is None:
      asset_class = self._guess_asset_class(asset_version.getAsset())

    asset_class_version = asset_class.version_io()
    if asset_version.getId() not in self._asset_versions_dict.keys():
      self._asset_versions_dict[asset_version.getId()] = asset_class_version(asset_version)
    return self._asset_versions_dict[asset_version.getId()]

  def get_asset_from_id(self, asset_id, asset_class=None):
    if asset_id == None:
      return

    if asset_id in self._assets_dict.keys():
      return self._assets_dict[asset_id]

    try:
      asset = Asset(asset_id)
    except FTrackError as err:
      if asset_class is not None:
        asset_name = asset_class.__name__.capitalize()
      else:
        asset_name = "Asset"
      error= "The current {0} Asset is incorrect [{1}]".format(asset_name,
                                                               str(err))
      raise AssetIOError(error)
    return self.get_asset(asset, asset_class)


  def get_version_from_id(self, asset_version_id, asset_class=None):
    if asset_version_id in self._asset_versions_dict.keys():
      return self._asset_versions_dict[asset_version_id]

    try:
      asset_version = AssetVersion(asset_version_id)
    except FTrackError as err:
      if asset_class is not None:
        asset_name = asset_class.__name__.capitalize()
      else:
        asset_name = "Asset"
      error= "The current {0} Asset is incorrect [{1}]".format(asset_name,
                                                               str(err))
      raise AssetIOError(error)
    return self.get_version(asset_version, asset_class)

  def get_asset_from_version_id(self, asset_version_id, asset_class=None):
    if asset_version_id == None:
      return
    try:
      asset_version = AssetVersion(asset_version_id)
      asset = asset_version.getAsset()
    except FTrackError as err:
      if asset_class is not None:
        asset_name = asset_class.__name__.capitalize()
      else:
        asset_name = "Asset"
      error= "The current {0} Asset is incorrect [{1}]".format(asset_name,
                                                               str(err))
      raise AssetIOError(error)
    return self.get_asset(asset, asset_class)

  def get_assets_from_task(self, task, asset_classes):
    from millftrack.cache import CachedEntity
    cached_assets = CachedEntity.getAssets(task)

    type_ids = dict()
    for asset_class in asset_classes:
      asset_name = asset_class.__name__.capitalize()
      connectors = asset_class.connectors()
      for connector in connectors:
        try:
          type_ids[AssetType(connector.asset_type).getId()] = asset_class
        except FTrackError as err:
          error= "The {0} Asset Type are incorrect or don't exist on the server [{1}]".format(asset_name.capitalize(),
                                                                                          str(err))
          raise AssetIOError(error)

    assets = []
    for asset in cached_assets:
      type_id = asset.get("typeid")
      if type_id in type_ids.keys():
        assets.append( self.get_asset(asset, type_ids[type_id]) )
    return assets


## AssetFactory singleton
N_AssetFactory = AssetFactory()
