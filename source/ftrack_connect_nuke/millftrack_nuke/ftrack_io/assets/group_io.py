#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError

import json

NODES_NUMBER_META = "mft.node_numbers"
LINKED_IDS_META = "mft.linked_ids"


class GroupIO(AssetIO):
  ''' Describe a group of nodes asset
  '''

  @staticmethod
  def version_io():
    return GroupVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import group
    return [ group.NukeGroupOfNodes() ]


class GroupVersionIO(AssetVersionIO):
  ''' Describe a group of nodes asset version
  '''

  def __init__(self, asset):
    super(GroupVersionIO, self).__init__(asset)

    # Cached meta
    self._linked_id = None

  @staticmethod
  def asset_io():
    return GroupIO

  def linked_id(self, node_name):
    if self._linked_id is None:
      try:
        self._linked_id = json.loads(self.ftrack_object.getMeta(LINKED_IDS_META))
      except:
        self._linked_id = dict()

    if node_name in self._linked_id.keys():
      return self._linked_id[node_name]

  def set_metadatas(self, nodes, versions_links_dict):
    all_nodes_dict = dict()
    linked_id_dict = dict()

    for node in nodes:
      version_id = None
      if node.name() in versions_links_dict.keys():
        version_id = versions_links_dict[node.name()].id

      if node.Class() not in all_nodes_dict.keys():
        all_nodes_dict[node.Class()] = [0, 0]
      all_nodes_dict[node.Class()][0] += 1

      if version_id is not None:
        all_nodes_dict[node.Class()][1] += 1
        linked_id_dict[node.name()] = version_id

    self.ftrack_object.setMeta(NODES_NUMBER_META, json.dumps(all_nodes_dict))
    self.ftrack_object.setMeta(LINKED_IDS_META, json.dumps(linked_id_dict))

  def set_links(self, versions_links):
    if len(versions_links) > 0:
      self.ftrack_object.addUsesVersions(versions=[v.ftrack_object for v in versions_links])
