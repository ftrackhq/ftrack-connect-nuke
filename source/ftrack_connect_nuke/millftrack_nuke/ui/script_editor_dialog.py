#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore

from generic.base_dialog import BaseDialog

from widgets.snapshots_widget import SnapshotsWidget
from widgets.comment_widget import CommentWidget


class ScriptEditorDialog(BaseDialog):

    def __init__(self, scene_version):
        # We need to set the activeWindow as parent to get the "refresh" button for
        # the snapshot working (For some reason it can't get it from a default
        # value..)
        super(ScriptEditorDialog, self).__init__(
            QtGui.QApplication.activeWindow())
        self.setFTrackTitle("Script editor...")

        self.setupUI()

        self.update_asset(scene_version)

        self.exec_()

    def setupUI(self):
        self.resize(620, 700)
        self.setMinimumWidth(620)
        self.setMinimumHeight(700)

        css_asset_name = "color: #c3cfa4; font-weight: bold;"
        css_asset_version = "color: #de8888; font-weight: bold;"
        css_asset_global = """
        QFrame { padding: 3px; border-radius: 4px;
                 background: #222; color: #FFF; font-size: 13px; }
        QLabel { padding: 0px; background: none; }
        """

        css_comment = """
        QTextEdit { border: 3px solid #252525; }
        QScrollBar { border: 0; border-radius: 6px;
                     background-color: #333; margin: 1px;}
        QScrollBar::handle {background: #222; border: 1px solid #111;}
        QScrollBar::sub-line, QScrollBar::add-line {height: 0px; width: 0px;}
        """

        asset_frame = QtGui.QFrame(self)
        asset_frame_layout = QtGui.QVBoxLayout(asset_frame)
        asset_frame_layout.setContentsMargins(0, 0, 0, 0)
        asset_frame_layout.setSpacing(10)

        asset_main_frame = QtGui.QFrame(self)
        asset_main_frame.setStyleSheet(css_asset_global)
        asset_main_frame_layout = QtGui.QHBoxLayout(asset_main_frame)
        asset_main_frame_layout.setSpacing(10)
        asset_name_lbl = QtGui.QLabel("Asset", self)
        self._asset_name = QtGui.QLabel("...", asset_frame)
        self._asset_name.setStyleSheet(css_asset_name)
        spacer_asset = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Minimum)

        asset_version_lbl = QtGui.QLabel("Version", asset_frame)
        self._asset_version = QtGui.QLabel("...", asset_frame)
        self._asset_version.setStyleSheet(css_asset_version)
        asset_main_frame_layout.addWidget(asset_name_lbl)
        asset_main_frame_layout.addWidget(self._asset_name)
        asset_main_frame_layout.addItem(spacer_asset)
        asset_main_frame_layout.addWidget(asset_version_lbl)
        asset_main_frame_layout.addWidget(self._asset_version)
        asset_frame_layout.addWidget(asset_main_frame)

        asset_setting_layout = QtGui.QVBoxLayout()
        asset_setting_layout.setContentsMargins(0, 0, 0, 0)
        asset_setting_layout.setSpacing(10)
        self._snapshotWidget = SnapshotsWidget(asset_frame)
        asset_setting_layout.addWidget(self._snapshotWidget)

        self._comment_widget = CommentWidget(asset_frame)
        self._comment_widget.changed.connect(self._validate)
        asset_setting_layout.addWidget(self._comment_widget)
        asset_frame_layout.addItem(asset_setting_layout)

        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum,
                                   QtGui.QSizePolicy.Expanding)
        asset_frame_layout.addItem(spacer)

        self.addContentWidget(asset_frame)

    def update_asset(self, scene_version):
        self._asset_name.setText(scene_version.getName())
        self._asset_version.setText("%03d" % scene_version.get('version'))

        if scene_version.comment is None:
            scene_version.regen_cache()

        self._comment_widget.set_text(scene_version.comment)

    @property
    def comment(self):
        return self._comment_widget.text

    @property
    def asset_thumbnail(self):
        return self._snapshotWidget.save_thumbnail()

    def _validate(self):
        pass
