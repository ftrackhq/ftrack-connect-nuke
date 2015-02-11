#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftrack
from FnAssetAPI import logging
import json

from ui.script_opener_dialog import ScriptOpenerDialog
from ui.script_editor_dialog import ScriptEditorDialog
from ui.script_publisher_dialog import ScriptPublisherDialog
from ui.gizmo_publisher_dialog import GizmoPublisherDialog
from ui.group_publisher_dialog import GroupPublisherDialog
from ui.warning_dialog import LockedSceneDialog
from ui.assets_dialog import AssetsLoaderDialog

from ftrack_connect_nuke.ftrackConnector.maincon import FTAssetObject
from ftrack_connect_nuke.ftrackConnector.nukeassets import GizmoAsset, NukeSceneAsset
from ftrack_connect_nuke.ftrackConnector.nukecon import Connector


from ui.images import image_dir


import os
import re

import nuke


class AssetsManager(object):

    def __init__(self):
        module_name = __name__ + "." + self.__class__.__name__
        self.recent_assets = RecentScenes(module_name)
        self.asset_locker = AssetLocker()

        self._loader_panel = None
        self.block_save_callback = False

    @staticmethod
    def get_current_scene_version_id():
        current_task = ftrack.Task(
            os.getenv('FTRACK_TASKID',
                      os.getenv('FTRACK_SHOTID'
                                )
                      )
        )
        return ftrack.Task(current_task).getId()

    @staticmethod
    def get_current_scene():
        version_id = AssetsManager.get_current_scene_version_id()
        if version_id == None:
            return

        try:
            scene_version = N_AssetFactory.get_version_from_id(
                version_id, SceneIO)
        except:
            logging.error("This asset doesn't exist [%s]" % version_id)
        else:
            return scene_version

    @staticmethod
    def open_script(asset_version_id):

        current_version_id = AssetsManager.get_current_scene_version_id()

        try:
            scene_version = N_AssetFactory.get_version_from_id(
                asset_version_id, SceneIO)
            if scene_version.id == current_version_id:
                return

        except:
            nuke.critical("This asset doesn't exist [%s]" % asset_version_id)
            return

        locker = scene_version.asset.locker
        if locker != None:
            nuke.critical("This asset is locked by %s [%s]" % (
                locker.getName(), locker.getEmail()))
        else:
            AssetsManager.load_gizmos_from_task(scene_version, 'scene')
            # scene_version.load_dependencies()

            scene_version.load_asset()

    def load_script(self, version):
        path = version.getComponent(name='scene').getFilesystemPath()
        nuke.nodePaste(path)

    def open_script_panel(self):
        version_id = AssetsManager.get_current_scene_version_id()

        panel = ScriptOpenerDialog(version_id)
        if panel.result():
            scene_version = panel.current_scene_version

            AssetsManager.load_gizmos_from_task(scene_version, 'scene')
            # scene_version.load_dependencies()
            self.load_script(scene_version)
            # scene_version.load_asset()

            # Update recent assets
            # self.recent_assets.add_scene(scene_version)
            self.recent_assets.update_menu()

    def publish_script_panel(self):
        task_id = AssetsManager.get_current_scene_version_id()

        panel = ScriptPublisherDialog(task_id)

        self.block_save_callback = True

        if panel.result():
            task = panel.current_task
            asset_name = panel.asset_name
            thumbnail = panel.asset_thumbnail
            comment = panel.comment
            asset_type = panel.current_asset_type

            import tempfile
            tmp_script = tempfile.NamedTemporaryFile(
                suffix='.nk', delete=False).name
            nuke.scriptSaveAs(tmp_script)

            task = ftrack.Task(task_id)
            parent = task.getParent()
            asset_id = parent.createAsset(
                name=asset_name,
                assetType=asset_type
            ).getId()

            asset = ftrack.Asset(asset_id)
            version = asset.createVersion(comment=comment, taskid=task.getId())
            version.createComponent(
                name='scene',
                path=tmp_script
            )

            version.createThumbnail(thumbnail)

            scene_metas = SceneNodeAnalyser()

            version.setMeta(
                'mft.node_numbers', json.dumps(scene_metas.node_number_meta))
            # version.set_links()

            result = version.publish()
            if result:
                nuke.message('Asset %s correctly published' % asset.getName())

            if panel.current_shot_status_changed():
                task.shot.ftrack_object.setStatus(panel.current_shot_status)

            if panel.current_task_status_changed():
                task.setStatus(panel.current_task_status)

            # self.recent_assets.add_scene(version)
            self.recent_assets.update_menu()

            #
            # nuke_connector = panel.connector
            # asset = nuke_connector.create( panel.asset_name, task.ftrack_object, task.shot.ftrack_object )
            # version = nuke_connector.saveVersion( asset, panel.comment, task.id,
            # thumbnail= panel.asset_thumbnail )

            # Update version links and metadatas
            # scene_version = N_AssetFactory.get_version_from_id(version.getId(), SceneIO)
            #
            # scene_version.set_metadatas()
            # scene_version.set_links()
            #
            # self.lock_scene_asset(scene_version)
            #
            # AssetsManager.load_gizmos_from_task(scene_version.asset.task.ftrack_object)
            #
            # Update recent assets

        self.block_save_callback = False

    def publish_gizmo_panel(self):

        task_id = AssetsManager.get_current_scene_version_id()
        panel = GizmoPublisherDialog(task_id)

        if panel.result():
            task = panel.current_task
            asset_name = panel.asset_name
            comment = panel.comment
            file_path = panel.gizmo_path

            task = ftrack.Task(task_id)
            parent = task.getParent()
            asset_id = parent.createAsset(
                name=asset_name,
                assetType='nuke_gizmo'
            ).getId()

            asset = ftrack.Asset(asset_id)
            version = asset.createVersion(comment=comment, taskid=task.getId())
            version.createComponent(
                name='gizmo',
                path=file_path
            )

            result = version.publish()
            if result:
                nuke.message('Asset %s correctly published' % asset.getName())

    def publish_group_panel(self):

        version_id = AssetsManager.get_current_scene_version_id()

        black_list = ["Viewer", "BackdropNode"]

        nodes = [
            n for n in nuke.selectedNodes() if n.Class() not in black_list]
        panel = GroupPublisherDialog(nodes, version_id)

        if panel.result():
            task = panel.current_task
            asset_name = panel.asset_name
            comment = panel.comment
            file_path = panel.nodes

            if not version_id:

                asset = task.getParent().createAsset(
                    name=asset_name,
                    assetType='nuke_group_nodes'
                )
                asset_version = asset.createVersion(
                    comment=comment, taskid=task.getId()
                )
                version_id = asset_version.getId()

            version = ftrack.AssetVersion(version_id)

            version.createComponent(
                name='node_group',
                path=file_path
            )
            version.publish()

            # group_connector = GroupIO.connectors()[0]
            # asset = group_connector.create( panel.asset_name, task.ftrack_object,
            #                                 task.shot.ftrack_object )
            # version = group_connector.saveVersion( asset, panel.comment, task.id,
            #                                        thumbnail= panel.asset_thumbnail,
            #                                        nodes= panel.nodes )

            # versions_links_dict =  panel.asset_version_nodes

            # group_version = N_AssetFactory.get_version(version, GroupIO)
            # group_version.set_metadatas(panel.nodes, versions_links_dict)
            # group_version.set_links(versions_links_dict.values())

    @staticmethod
    def load_gizmos_from_task(version, component='gizmo'):
        gizmo_path = version.getComponent(component).getFilesystemPath()
        if gizmo_path != None:
            nuke.pluginAddPath(os.path.dirname(gizmo_path))

    @staticmethod
    def set_gizmos_to_toolbar():
        version_id = AssetsManager.get_current_scene_version_id()
        if version_id == None:
            return

        try:
            scene_version = N_AssetFactory.get_version_from_id(
                version_id, SceneIO)
        except:
            logging.error(
                "This asset doesn't exist [%s]" % version_id, "FTrack")
            return

        task_object = scene_version.asset.task.ftrack_object
        gizmos = N_AssetFactory.get_assets_from_task(task_object, [GizmoIO])

        toolbar = nuke.toolbar("Nodes")
        project_menu = toolbar.menu("Ftrack Task")
        if project_menu == None:
            icon = os.path.join(image_dir, "mill_toolbar_menu.png")
            project_menu = toolbar.addMenu("Ftrack Task", icon=icon)

        for gizmo in gizmos:
            last_version = gizmo.versions[-1]
            gizmo_version = N_AssetFactory.get_version(last_version, GizmoIO)
            name = " - ".join(gizmo.task.parents_list) + \
                "/" + gizmo_version.name
            project_menu.addCommand(name, gizmo_version.load_asset,
                                    tooltip=gizmo_version.comment)

    def update_script(self):
        if self.block_save_callback:
            return

        scene_version = AssetsManager.get_current_scene()
        if scene_version == None:
            return

        self.block_save_callback = True

        panel = ScriptEditorDialog(scene_version)

        if panel.result():
            scene_version.edit(
                panel.user_id, panel.comment, panel.asset_thumbnail)
            scene_version.set_metadatas()
            scene_version.set_links()

            scene_version.regen_image_cache = True

        self.block_save_callback = False

        if not panel.result():
            raise Exception("Script edition cancelled")

    def lock_scene_asset(self, scene_version=None):
        if scene_version == None:
            scene_version = AssetsManager.get_current_scene()
            if scene_version == None:
                return

        scene_version.asset.lock_asset(True)
        self.asset_locker.lock_asset(scene_version.asset.id, True)

    def unlock_scene_asset(self, scene_version=None):
        if scene_version == None:
            scene_version = AssetsManager.get_current_scene()
            if scene_version == None:
                return

        scene_version.asset.lock_asset(False)
        self.asset_locker.lock_asset(scene_version.asset.id, False)

    def management_panel(self):
        if self._loader_panel == None:
            version_id = AssetsManager.get_current_scene_version_id()
            self._loader_panel = AssetsLoaderDialog(version_id)
        self._loader_panel.show()

    def drop_asset_to_dag(self, mime_type, asset_info):
        if mime_type != "text/plain":
            return False

        try:
            id_ftrack, asset_name, asset_version_id = asset_info.split(":", 2)
        except ValueError:
            return False

        if id_ftrack != "FTRACK_DROP_ACTION":
            return False

        droppable_assets = [ImageIO, GizmoIO, GroupIO]

        asset_class = None
        for droppable_asset in droppable_assets:
            if droppable_asset.__name__ == asset_name:
                asset_class = droppable_asset

        if asset_class is None:
            msg = "Impossible to drop this asset, the asset IO class{0} \
isn't recognised".format(asset_name)
            nuke.message(msg)
            logging.error(msg)

        try:
            version = N_AssetFactory.get_version_from_id(
                asset_version_id, asset_class)
            version.load_asset()
        except Exception as err:
            msg = "Impossible to drop this asset: [{0}]".format(err)
            nuke.message(msg)
            logging.error(msg)

        return True


class AssetLocker(object):

    def __init__(self):
        self._pattern_locker = "._ftrack_locked_asset%03d"
        self.nuke_perso = self._get_personal_folder()

    def _get_personal_folder(self):
        home = os.getenv('HOME')
        if home == None or not os.path.isdir(home):
            error = "The environment variable 'HOME' is incorrect.. [%s]" % str(
                home)
            logging.error(error)
            return

        nuke_perso = os.path.join(home, '.nuke')
        if not os.access(nuke_perso, os.W_OK):
            error = "Impossible to access '%s', please contact RnD." % nuke_perso
            logging.error(error)
            return

        return nuke_perso

    def _get_locked_dict(self):
        locker_files = []
        locker_dict = dict()

        index = 1
        while os.path.isfile(os.path.join(self.nuke_perso, self._pattern_locker % index)):
            locker_files.append(self._pattern_locker % index)
            index += 1

        for locker_file in locker_files:
            locker_file_path = os.path.join(self.nuke_perso, locker_file)
            if not os.access(locker_file_path, os.W_OK):
                error = "Impossible to access '%s', please contact RnD." % locker_file
                logging.error(error)

            else:
                try:
                    f = open(locker_file_path, "r")
                    locked_id = f.read().strip()
                    f.close()
                except Exception as err:
                    error = "Impossible to open '%s' [%s]" % (
                        locker_file, str(err))
                    logging.error(error)
                    continue

                if (re.search("^[a-zA-Z0-9-]+$", locked_id) == None
                        or locked_id in locker_dict.keys()):
                    os.remove(locker_file_path)

                else:
                    locker_dict[locked_id] = locker_file_path

        return locker_dict

    def lock_asset(self, asset_id, bool_value):
        locker_dict = self._get_locked_dict()

        if bool_value:
            if asset_id in locker_dict.keys():
                return

            index = 1
            while os.path.isfile(os.path.join(self.nuke_perso, self._pattern_locker % index)):
                index += 1

            locker_file_path = os.path.join(
                self.nuke_perso, self._pattern_locker % index)
            try:
                f = open(locker_file_path, "w")
                f.write(asset_id)
                f.close()
            except Exception as err:
                error = "Impossible to open '%s' [%s]" % (
                    locker_file_path, str(err))
                logging.error(error)
            os.chmod(locker_file_path, 0777)

        else:
            if asset_id not in locker_dict.keys():
                return

            try:
                os.remove(locker_dict[asset_id])
            except:
                error = "Impossible to remove '%s' [%s]" % (
                    locker_dict[asset_id], str(err))
                logging.error(error)

    def check_locked_scenes(self):
        locker_dict = self._get_locked_dict()
        if len(locker_dict) == 0:
            return

        panel = LockedSceneDialog(locker_dict.keys())
        if panel.result():
            for scene_id in panel.ids_to_remove:
                if os.access(locker_dict[scene_id], os.W_OK):
                    os.remove(locker_dict[scene_id])
                    logging.info("unlocked %s" % scene_id)
            panel.unlock_selected_assets()


class RecentScenes(object):

    def __init__(self, ftrack_module_name):
        self.ftrack_module_name = ftrack_module_name
        self.config_file = self._get_config_file()
        self.menu = None

    def _get_task_parents(self, task):
        task = ftrack.Task(task)
        parents = [t.getName() for t in task.getParents()]
        parents.reverse()
        parents.append(task.getName())
        parents = ' / '.join(parents)
        return parents

    def _get_config_file(self):
        home = os.getenv('HOME')
        if home == None or not os.path.isdir(home):
            error = "The environment variable 'HOME' is incorrect.. [%s]" % str(
                home)
            logging.error(error)
            return

        nuke_folder_perso = os.path.join(home, '.nuke')
        config_file = os.path.join(nuke_folder_perso, 'ftrack_recent_scenes')
        if not os.access(nuke_folder_perso, os.W_OK):
            error = "Impossible to access '%s', please contact RnD." % nuke_folder_perso
            logging.error(error)
            return

        if (os.path.isfile(config_file)
                and not os.access(config_file, os.W_OK)):
            error = "Impossible to access '%s', please contact RnD." % config_file
            logging.error(error)
            return

        return config_file

    # def add_scene(self, scene_version):
    #   recents_list = self._get_list()
    #   if recents_list == None:
    #     error = "Impossible to add this asset to the 'Recent scenes' list. Please contact RnD."
    #     logging.error(error)
    #     return

    #   version_nb = " v%02d" % scene_version.get('version')

    #   name = scene_version.asset.task.parents + " / " + scene_version.name + version_nb
    #   tuple_asset = (scene_version.getId(), name)
    #   recents_list = [tuple_asset] + recents_list

    #   self._write_list(recents_list)

    def update_menu(self):
        if self.menu == None:
            return

        self.menu.clearMenu()
        recents_list = self._get_list()
        if recents_list == None:
            error = "Impossible to get the 'Recent scenes' list. Please contact RnD."
            logging.error(error)
            return

        for asset_id, asset_name in recents_list:
            command = self.ftrack_module_name + ".open_script('%s')" % asset_id
            self.menu.addCommand(asset_name, command)

    def _get_list(self):
        if self.config_file == None:
            return

        recents = []
        if os.path.isfile(self.config_file):
            f = open(self.config_file, "r")
            max_recent = 10
            for line in f.readlines():
                if max_recent == 0:
                    break

                line = line.rsplit('\n')[0].strip()
                names = re.findall("(?<=\')[^\']*?(?=\'$)", line)
                if len(names) < 1 or len(names) > 1:
                    continue

                name_version = names[0]
                lines = [elt for elt in line.split(
                    "'" + name_version + "'") if len(elt) != 0]
                if len(lines) < 1 or len(lines) > 1:
                    continue

                id_version = lines[0].strip()
                asset_tuple = (id_version, name_version)
                recents.append(asset_tuple)
                max_recent -= 1

            f.close()

        return recents

    def _write_list(self, recents_list):
        if self.config_file == None:
            error = "Impossible to add this asset to the 'Recent scenes' list. Please contact RnD."
            logging.error(error)
            return

        recent_scenes_lines = []
        for id, name in recents_list:
            line = id + " '" + name.replace(" / ", " \/ ") + "'"
            if line not in recent_scenes_lines:
                recent_scenes_lines.append(line)

        f = open(self.config_file, "w")
        f.write("\n".join(recent_scenes_lines))
        f.close()


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
        self._outputs = ["Write", "MillWrite", "MillWrite2", "MillWrite3"]
        self._inputs = ["Read", "ReadGeo"]
        self._blacklist_classes = ["Dot", "BackdropNode", "Viewer"]

        self._nodes_metas = [
            NodeType(
                "Output nodes", "^(" + "|".join(self._outputs) + ")$", is_output=True),
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
            # If there is no 'disable' knob, we consider the node is enabled
            except:
                node_enabled = True
            if node_enabled:
                all_enabled_nodes.append(node.name())

            all_nodes.append(node.name())

        all_nodes_in_tree = self._nodes_in_tree(self._nodes_metas[0].nodes,
                                                blacklist_nodes)

        self.node_number_meta = {"Nodes number": (len(all_nodes),
                                                  len(all_enabled_nodes),
                                                  len(all_nodes_in_tree),
                                                  len(all_tracked_nodes))}
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
