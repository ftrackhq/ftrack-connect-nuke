#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..asset import AssetIO, AssetVersionIO
from ..asset import AssetIOError
from ..asset import N_AssetFactory

from ftrack import User, FTrackError

import re
import datetime
import json

from ...controller import Controller
from ...logger import FT_logger
from ... import utilities

import nuke

NODES_NUMBER_META = "mft.node_numbers"
LAST_EDIT = "mft.last_edit"


class SceneIO(AssetIO):
  ''' Describe a Nuke Scene asset (file ending with ".nk")
  '''

  def __init__(self, asset):
    super(SceneIO, self).__init__(asset)

    # Cached meta from versions ID
    self._metas = dict()

  @staticmethod
  def version_io():
    return SceneVersionIO

  @staticmethod
  def connectors():
    from millftrack.nuke.asset_types import scene
    return [ scene.NukeSceneComp(),
             scene.NukeScenePrecomp(),
             scene.NukeSceneRoto() ]

  def get_nodes_number_meta(self, ftrack_version):
    if ftrack_version.getId() not in self._metas.keys():
      try:
        meta_dict_decoded = json.loads(ftrack_version.getMeta(NODES_NUMBER_META))
      except:
        meta_dict_decoded = None
      if meta_dict_decoded.__class__ is not dict:
        meta_dict_decoded = None

      self._metas[ftrack_version.getId()] = meta_dict_decoded
    return self._metas[ftrack_version.getId()]


class SceneVersionIO(AssetVersionIO):
  ''' Describe a Nuke Scene asset version
  '''

  @staticmethod
  def asset_io():
    return SceneIO

  @property
  def web_widget_infos_Url(self):
    return self.ftrack_object.getWebWidgetUrl(name="info")

  @property
  def previous_versions(self):
    return self.asset.versions[:self.version_number]

  def set_metadatas(self):
    scene_metas = SceneNodeAnalyser()
    self.ftrack_object.setMeta( NODES_NUMBER_META,
                                json.dumps(scene_metas.node_number_meta) )

  def set_links(self):
    links = set()
    for node in nuke.allNodes(group=nuke.root()):
      if "ftrack_version_id" in node.knobs().keys():
        links.add(node.knobs()["ftrack_version_id"].value())

    if "ftrack_links" in nuke.root().knobs().keys():
      nuke.root().knobs()["ftrack_links"].setValue("\n".join(links))

    linked_versions = []
    for link_id in links:
      try:
        version = N_AssetFactory.get_version_from_id(link_id)
        linked_versions.append(version.ftrack_object)
      except AssetIOError as err:
        pass

    nuke.scriptSave()
    self.ftrack_object.addUsesVersions(versions=linked_versions)

  def edit(self, user_id, comment, thumbnail):
    now = datetime.datetime.now(utilities.SERVER_TIME)
    date_list = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    self.ftrack_object.setMeta(LAST_EDIT, json.dumps([user_id, date_list]))

    self.ftrack_object.set("comment", comment)
    self.ftrack_object.createThumbnail(thumbnail)

    controller = Controller(self.regen_cache)
    controller.start()

  def editor(self):
    meta = self.ftrack_object.getMeta(LAST_EDIT)
    if meta is None:
      return None

    try:
      user_id, date_list = json.loads(meta)
      date = datetime.datetime(date_list[0], date_list[1], date_list[2],
                               date_list[3], date_list[4], date_list[5])
    except Exception as err:
      FT_logger.error("The editor metadata is incorrect [{0}]".format(err))
      return None

    try:
      user = User(user_id)
    except FTrackError:
      FT_logger.error("The user id does not exist [{0}]".format(user_id))
      return None

    return (user, utilities.date_with_tz(date))


class NodeType(object):
  def __init__(self, name, regex=None, is_output=False):
    self.name = name
    self.is_output = is_output

    self._total_ftrack_assets_ids = []

    if regex is not None:
      self._regex = re.compile(regex)
    else:
      self._regex = re.compile("^" + name + "$")

    self.nodes = []

  def add_instance(self, node, id_ftrack=None):
    self.nodes.append(node)

    if id_ftrack is not None:
      self._total_ftrack_assets_ids.append(id_ftrack)

  def match(self, node_class):
    return re.search(self._regex, node_class) is not None

  def compute_total(self, all_enabled_nodes, all_nodes_in_tree):
    node_names = set([n.name() for n in self.nodes])

    total = len(node_names)
    total_enabled = len(node_names.intersection(all_enabled_nodes))
    total_in_tree = 0

    if self.is_output:
      return (total, total_enabled)

    total_in_tree = len(node_names.intersection(all_nodes_in_tree))
    total_tracked = len(self._total_ftrack_assets_ids)
    return (total, total_enabled, total_in_tree, total_tracked)


class SceneNodeAnalyser(object):

  ''' List the useful nodes composing the Nuke scene '''

  def __init__(self):
    self._outputs = [ "Write", "MillWrite", "MillWrite2", "MillWrite3" ]
    self._inputs = [ "Read", "ReadGeo" ]
    self._blacklist_classes = [ "Dot", "BackdropNode", "Viewer" ]

    self._nodes_metas = [
      NodeType("Output nodes", "^(" + "|".join(self._outputs) + ")$", is_output=True),
      NodeType("Input nodes", "^(" + "|".join(self._inputs) + ")$"),
      NodeType("Genarts nodes", "^OFXcom.genarts."),
      NodeType("Revision nodes", "^OFXcom.revisionfx."),
      NodeType("VectorBlur nodes"),
      NodeType("OpticalFlares nodes")
    ]

    self.links = set()

    all_nodes = []
    all_enabled_nodes = []
    all_tracked_nodes = []

    blacklist_nodes = []

    for node in nuke.allNodes(group=nuke.root()):
      if node.Class() in self._blacklist_classes:
        blacklist_nodes.append(node.name())
        continue

      id_ftrack = None
      if "ftrack_version_id" in node.knobs().keys():
        id_ftrack = node["ftrack_version_id"].value()
        nuke.tprint(id_ftrack)
        all_tracked_nodes.append(id_ftrack)

      for node_meta in self._nodes_metas:
        if node_meta.match(node.Class()):
          node_meta.add_instance(node, id_ftrack)

      try:
        node_enabled = not node["disable"].value()
      except: # If there is no 'disable' knob, we consider the node is enabled
        node_enabled = True
      if node_enabled:
        all_enabled_nodes.append(node.name())

      all_nodes.append(node.name())

    all_nodes_in_tree = self._nodes_in_tree( self._nodes_metas[0].nodes,
                                             blacklist_nodes )


    self.node_number_meta = { "Nodes number" : ( len(all_nodes),
                                                 len(all_enabled_nodes),
                                                 len(all_nodes_in_tree),
                                                 len(all_tracked_nodes) ) }
    for node_meta in self._nodes_metas:
      self.node_number_meta[node_meta.name] = node_meta.compute_total(all_enabled_nodes,
                                                                      all_nodes_in_tree)

    nuke.tprint(self.node_number_meta)

  def _nodes_in_tree(self, outputs, blacklist_nodes):
    tree = set()

    for output in outputs:
      deps = set()
      if output["disable"].value():
        continue
      children = nuke.dependencies(output)
      while len(children) != 0:
        new_children = []
        for child in children:
          new_children += nuke.dependencies(child)
        deps = deps.union([c.name() for c in children])
        children = new_children
      deps_valid = deps.difference(blacklist_nodes)
      tree = tree.union(deps_valid)

    return tree
