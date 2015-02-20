#!/usr/bin/env python

from PySide import QtGui, QtCore

from generic.base_dialog import BaseDialog

class LockedSceneDialog(BaseDialog):

    def __init__(self, scenes_ids, parent=None):
        super(LockedSceneDialog, self).__init__(parent)
        self.setFTrackTitle("Scene Asset(s) locked...")

        self.resize(500, 200)
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        box_css = """
      QScrollBar { border: 0; border-radius: 6px; background-color: #333;
                   margin: 1px; }
      QScrollBar::handle { background: #222; border: 1px solid #111; }
      QScrollBar::sub-line, QScrollBar::add-line { height: 0px; width: 0px; }
      QListView { padding: 0px; border: 2px solid #222;
                  border-radius: 3px; background: #555; }
      QListView::item { background: #555; }
    """
        self.setStyleSheet(box_css)

        self._scene_names_dict = dict()

        self._incorrect_ids = []
        self._scenes_to_process = []

        for scene_id in scenes_ids:
            try:
                scene = N_AssetFactory.get_asset_from_id(scene_id, SceneIO)
                if scene.locker.getId() == self._user.getId():
                    self._scene_names_dict[self._get_scene_name(scene)] = scene
                    self._scenes_to_process.append(scene)
                else:
                    self._incorrect_ids.append(scene_id)
            except Exception as err:
                self._incorrect_ids.append(scene_id)
                continue

        info = "Some scenes asset you recently opened are still locked by you. If \
you are currently working on it, please ignore this message. However, if you \
experienced a crash, this asset must be unlocked.\n\
Please check carefully the list below:"
        info_lbl = QtGui.QLabel(info, self)
        info_lbl.setWordWrap(True)
        info_lbl.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.addContentWidget(info_lbl)

        self.assets_list = QtGui.QListWidget(self)
        self.addContentWidget(self.assets_list)

        self._save_btn.setText("Unlock assets")

        for scene in self._scenes_to_process:
            item = QtGui.QListWidgetItem(
                self._get_scene_name(scene), self.assets_list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.assets_list.addItem(item)

        self.exec_()

    def _get_scene_name(self, scene_asset):
        return scene_asset.task.parents + " / " + scene_asset.name

    @property
    def ids_to_remove(self):
        ids_to_remove = self._incorrect_ids
        for i in range(self.assets_list.count()):
            item = self.assets_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                asset = self._scene_names_dict[item.text()]
                ids_to_remove.append(asset.id)
        return ids_to_remove

    def unlock_selected_assets(self):
        for i in range(self.assets_list.count()):
            item = self.assets_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                asset = self._scene_names_dict[item.text()]
                asset.lock_asset(False)
