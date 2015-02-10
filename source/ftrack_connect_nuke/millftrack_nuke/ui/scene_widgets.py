#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore, QtWebKit
import ftrack
from generic.dockable_widget import BaseDockableWidget
from widgets.scene_stats_widget import StatisticWidget
from widgets.message_widget import MessageWidget
from widgets.status_widget import StatusWidget

# from ..ftrack_io.task import TaskIO
# from ..ftrack_io.asset import N_AssetFactory
# from ..ftrack_io.asset import AssetIOError

# from ..ftrack_io.assets.scene_io import SceneIO

from images import image_dir

from FnAssetAPI import logging

from .. import utilities

import nuke
import os


class SceneManagerWidget(BaseDockableWidget):

    def __init__(self, parent=None):
        super(SceneManagerWidget, self).__init__(parent)
        self.setupUI()

        nuke.addOnScriptLoad(self.refresh)
        nuke.addOnScriptSave(self.refresh)

        self.refresh()

    def setupUI(self):
        self.setMinimumWidth(400)

        widget = QtGui.QWidget(self)
        main_layout = QtGui.QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._webview = QtWebKit.QWebView()
        self._webview_empty = QtWebKit.QWebView()

        self._stackLayout = QtGui.QStackedLayout()
        self._stackLayout.addWidget(self._webview)
        self._stackLayout.addWidget(self._webview_empty)
        main_layout.addLayout(self._stackLayout)

        self._stackLayout.setCurrentWidget(self._webview_empty)
        self.addContentWidget(widget)

        self._refresh_btn = QtGui.QPushButton("Refresh", widget)
        self._refresh_btn.clicked.connect(self.refresh)
        self.addContentWidget(self._refresh_btn)

    def _get_meta(self, knob_name):
        if knob_name in nuke.root().knobs().keys():
            return nuke.root()[knob_name].value()

    def refresh(self):
        self.initiate_error_box()

        version_id = self._get_meta("ftrack_version_id")
        if version_id == None:
            msg = "This script is not an asset and does not belong to any tasks. "
            msg += "Please publish it in order to manage the corresponding task. "
            detail = "File > Mill Ftrack - Publish Script"
            self.set_error(msg, detail)
            self._stackLayout.setCurrentWidget(self._webview_empty)
            return

        try:
            current_scene_version = N_AssetFactory.get_version_from_id(
                version_id, SceneIO)
        except AssetIOError as err:
            msg = "The Version Asset ID of this script is incorrect. Please contact RnD."
            detail = "Version Asset ID : %s\nError: %s" % (
                version_id, str(err))
            self.set_error(msg, detail)
            self._stackLayout.setCurrentWidget(self._webview_empty)
            return

        url = QtCore.QUrl(current_scene_version.web_widget_infos_Url)
        if not url.isValid():
            msg = "The asset version Url 'info' is incorrect."
            self.set_error(msg)
            self._stackLayout.setCurrentWidget(self._webview_empty)
            return

        self._webview.load(url)
        self._stackLayout.setCurrentWidget(self._webview)


class SceneVersionWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(SceneVersionWidget, self).__init__(parent)
        self.setupUI()

        self._scene_versions_dict = dict()

    def setupUI(self):
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._empty_asset_version = NoSceneVersionWidget(self)
        self._loading_asset_version = LoadingSceneVersionWidget(self)
        self._stackLayout = QtGui.QStackedLayout()
        self._stackLayout.addWidget(self._empty_asset_version)
        self._stackLayout.addWidget(self._loading_asset_version)
        main_layout.addLayout(self._stackLayout)

        self.initiate()

    def initiate(self):
        self._stackLayout.setCurrentWidget(self._loading_asset_version)
        self._loading_asset_version.start_anim()

    def set_empty(self):
        self._stackLayout.setCurrentWidget(self._empty_asset_version)
        self._loading_asset_version.stop_anim()

    def set_scene_version(self, scene_version):
        # if scene_version.is_being_cached:
        #     return

        if scene_version.getId() not in self._scene_versions_dict.keys():
            widget = SingleSceneVersionWidget(scene_version, self)
            self._scene_versions_dict[scene_version.getId()] = widget
            self._stackLayout.addWidget(widget)

        self._stackLayout.setCurrentWidget(
            self._scene_versions_dict[scene_version.getId()])
        self._loading_asset_version.stop_anim()

    @property
    def current_scene_version(self):
        widget = self._stackLayout.currentWidget()
        return widget.scene_version

    def is_being_loaded(self):
        return self._stackLayout.currentWidget() == self._loading_asset_version

    def is_error(self):
        if self._stackLayout.currentWidget() == self._empty_asset_version:
            return True
        widget = self._stackLayout.currentWidget()
        return widget.error

    def is_locked(self):
        widget = self._stackLayout.currentWidget()
        return widget.locked


class NoSceneVersionWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(NoSceneVersionWidget, self).__init__(parent)
        self.setMinimumWidth(700)

        css_loading = """
        background:#222; border-radius: 4px;
        padding:10px; border: 0px;
        """

        image = os.path.join(image_dir, "no_asset.png")
        css_image = """
        background: url(""" + image + """) no-repeat center center;
        """
        main_layout = QtGui.QHBoxLayout(self)

        frame = QtGui.QFrame(self)
        frame.setMaximumSize(QtCore.QSize(350, 400))
        frame.setStyleSheet(css_loading)
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setFrameShadow(QtGui.QFrame.Raised)
        frame_layout = QtGui.QVBoxLayout(frame)

        movie_screen = QtGui.QFrame(frame)
        movie_screen.setMinimumSize(QtCore.QSize(300, 300))
        movie_screen.setStyleSheet(css_image)

        warning = QtGui.QLabel(frame)
        warning.setText("No scene asset found for this task...")
        warning.setWordWrap(True)
        warning.setAlignment(QtCore.Qt.AlignCenter)

        frame_layout.addWidget(movie_screen)
        frame_layout.addWidget(warning)

        main_layout.addWidget(frame)


class LoadingSceneVersionWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(LoadingSceneVersionWidget, self).__init__(parent)
        self.setMinimumWidth(700)

        css_loading = """
        background:#222; border-radius: 4px;
        padding:10px; border: 0px;
        """

        main_layout = QtGui.QHBoxLayout(self)

        frame = QtGui.QFrame(self)
        frame.setMaximumSize(QtCore.QSize(300, 250))
        frame.setStyleSheet(css_loading)
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setFrameShadow(QtGui.QFrame.Raised)
        frame_layout = QtGui.QVBoxLayout(frame)

        loading_gif = os.path.join(image_dir, "mill_logo_light.gif")
        self.movie = QtGui.QMovie(loading_gif, QtCore.QByteArray(), frame)

        movie_screen = QtGui.QLabel(frame)
        movie_screen.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        movie_screen.setAlignment(QtCore.Qt.AlignCenter)

        warning = QtGui.QLabel(frame)
        warning.setText("Loading scene asset...")
        warning.setWordWrap(True)
        warning.setAlignment(QtCore.Qt.AlignCenter)

        frame_layout.addWidget(movie_screen)
        frame_layout.addWidget(warning)

        main_layout.addWidget(frame)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        movie_screen.setMovie(self.movie)

    def start_anim(self):
        self.movie.start()

    def stop_anim(self):
        self.movie.stop()


class ThumbnailWidget(QtGui.QLabel):

    def __init__(self, parent=None, image=None):
        super(ThumbnailWidget, self).__init__(parent)
        css_thumbnail = """
        background: #000; border-radius: 2px;
        border: 1px solid #AAA;
        """
        self.size = QtCore.QSize(354, 236)
        self.setMinimumSize(self.size)
        self.setMaximumSize(self.size)

        self.setStyleSheet(css_thumbnail)
        self.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.update_image(image)

    def update_image(self, image_path=None):
        if image_path is None:
            from ..ftrack_io.asset import AssetVersionIO
            image_path = AssetVersionIO.default_thumbnail()
        self._pixmap = QtGui.QPixmap(image_path)
        pixmap_scaled = self._pixmap.scaled(
            self.size, QtCore.Qt.KeepAspectRatio)
        self.setPixmap(pixmap_scaled)


class SingleSceneVersionWidget(QtGui.QWidget):

    def __init__(self, scene_version=None, parent=None):
        super(SingleSceneVersionWidget, self).__init__(parent)
        self.scene_version = scene_version

        # self._scenes_connectors = SceneIO.connectors()

        self.error = False
        self.locked = False

        self.setupUI()
        self.initiate_scene_version()

    def setupUI(self):
        css_asset_global = """
        QFrame { padding: 3px; border-radius: 4px;
                 background: #222; color: #FFF; font-size: 13px; }
        QLabel { padding: 0px; background: none; }
        """
        self._css_lbl = "color: #AAA;"
        css_asset_name = "color: #c3cfa4; font-weight: bold;"
        css_asset_version = "color: #de8888; font-weight: bold;"
        css_comment = """
        color: #f0f0f0; background: #444; padding: 3px ; border-radius: 2px;
        """
        self._css_value = "color: #FFF; text-decoration: none;"

        self.setMinimumWidth(700)

        asset_frame_layout = QtGui.QVBoxLayout(self)
        asset_frame_layout.setContentsMargins(0, 0, 0, 0)
        asset_frame_layout.setSpacing(10)

        asset_main_frame = QtGui.QFrame(self)
        asset_main_frame.setStyleSheet(css_asset_global)
        asset_main_frame_layout = QtGui.QHBoxLayout(asset_main_frame)
        asset_main_frame_layout.setSpacing(10)
        asset_name_lbl = QtGui.QLabel("Asset", asset_main_frame)
        self._asset_name = QtGui.QLabel("...", asset_main_frame)
        self._asset_name.setStyleSheet(css_asset_name)
        spacer_asset = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Minimum)

        asset_version_lbl = QtGui.QLabel("Version", asset_main_frame)
        self._asset_version = QtGui.QLabel("...", asset_main_frame)
        self._asset_version.setStyleSheet(css_asset_version)
        asset_main_frame_layout.addWidget(asset_name_lbl)
        asset_main_frame_layout.addWidget(self._asset_name)
        asset_main_frame_layout.addItem(spacer_asset)
        asset_main_frame_layout.addWidget(asset_version_lbl)
        asset_main_frame_layout.addWidget(self._asset_version)
        asset_frame_layout.addWidget(asset_main_frame)

        self._scene_error_box = MessageWidget(self)
        asset_frame_layout.addWidget(self._scene_error_box)
        self._scene_error_box._warning_header.setWordWrap(True)
        self._scene_error_box._warning_header.setTextFormat(QtCore.Qt.RichText)

        self._scene_warning_box = MessageWidget(self)
        asset_frame_layout.addWidget(self._scene_warning_box)
        self._scene_warning_box._warning_header.setWordWrap(True)
        self._scene_warning_box._warning_header.setTextFormat(
            QtCore.Qt.RichText)

        overview_layout = QtGui.QHBoxLayout()
        overview_layout.setContentsMargins(0, 0, 0, 0)
        overview_layout.setSpacing(10)

        self._thumbnail_widget = ThumbnailWidget(self)
        overview_layout.addWidget(self._thumbnail_widget)

        self._infos_layout = QtGui.QFormLayout()
        self._infos_layout.setContentsMargins(0, 0, 0, 0)
        self._infos_layout.setSpacing(10)

        asset_type_lbl = QtGui.QLabel("Asset type", self)
        asset_type_lbl.setStyleSheet(self._css_lbl)
        self._asset_type = QtGui.QLabel(self)
        self.set_asset_type("...")
        status_lbl = QtGui.QLabel("Status", self)
        status_lbl.setStyleSheet(self._css_lbl)
        self._status = StatusWidget(ftrack.getTaskStatuses(), self)
        self._status.set_read_only(True)

        publish_lbl = QtGui.QLabel("Published by", self)
        publish_lbl.setStyleSheet(self._css_lbl)
        self._owner = QtGui.QLabel("...", self)
        self._owner.setTextFormat(QtCore.Qt.RichText)
        self._owner.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self._owner.setOpenExternalLinks(True)
        date_lbl = QtGui.QLabel("on", self)
        date_lbl.setStyleSheet(self._css_lbl)
        self._date = QtGui.QLabel(self)
        self._date.setStyleSheet(self._css_value)

        self._editor = None
        self._date_edit = None

        availability_lbl = QtGui.QLabel("Availability", self)
        availability_lbl.setStyleSheet(self._css_lbl)
        self._availability = QtGui.QLabel(self)
        self._availability.setStyleSheet(self._css_value)
        comment_lbl = QtGui.QLabel("Comment", self)
        comment_lbl.setStyleSheet(self._css_lbl)
        self._comment = QtGui.QLabel("...", self)
        self._comment.setWordWrap(True)
        self._comment.setStyleSheet(css_comment)

        self._infos_layout.setWidget(
            0, QtGui.QFormLayout.LabelRole, asset_type_lbl)
        self._infos_layout.setWidget(
            0, QtGui.QFormLayout.FieldRole, self._asset_type)
        self._infos_layout.setWidget(
            1, QtGui.QFormLayout.LabelRole, status_lbl)
        self._infos_layout.setWidget(
            1, QtGui.QFormLayout.FieldRole, self._status)
        self._infos_layout.setWidget(
            2, QtGui.QFormLayout.LabelRole, publish_lbl)
        self._infos_layout.setWidget(
            2, QtGui.QFormLayout.FieldRole, self._owner)
        self._infos_layout.setWidget(3, QtGui.QFormLayout.LabelRole, date_lbl)
        self._infos_layout.setWidget(
            3, QtGui.QFormLayout.FieldRole, self._date)
        self._infos_layout.setWidget(
            4, QtGui.QFormLayout.LabelRole, availability_lbl)
        self._infos_layout.setWidget(
            4, QtGui.QFormLayout.FieldRole, self._availability)
        self._infos_layout.setWidget(
            5, QtGui.QFormLayout.LabelRole, comment_lbl)
        self._infos_layout.setWidget(
            5, QtGui.QFormLayout.FieldRole, self._comment)
        overview_layout.addItem(self._infos_layout)

        spacer_overview = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Minimum)
        overview_layout.addItem(spacer_overview)
        asset_frame_layout.addItem(overview_layout)

        self._tab_widget = QtGui.QTabWidget(self)
        css_tab = """
    QTabWidget::pane { border-top: 2px solid #151515; top: -2px;
                       border-top-left-radius: 0px;
                       border-top-right-radius: 0px;
                       background: #282828; }
    QTabBar::tab { padding: 6px 10px; background: #151515;
                   border-top: 2px solid #151515;
                   border-right: 2px solid #151515;
                   border-left: 2px solid #151515;
                   border-radius: 0px; }
    QTabBar::tab:selected { background: #333;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px; }
    QTabBar::tab:hover { background: #222; }
    QTabBar::tab:!selected { margin-top: 2px; }
    """
        self._tab_widget.setStyleSheet(css_tab)

        # Display asset history

        tab_asset_history = QtGui.QWidget()
        tab_asset_history_layout = QtGui.QVBoxLayout(tab_asset_history)
        tab_asset_history_layout.setContentsMargins(0, 8, 0, 0)
        self._graph_widget = StatisticWidget(self.scene_version, self)
        tab_asset_history_layout.addWidget(self._graph_widget)
        self._tab_widget.addTab(tab_asset_history, "Asset history")

        # Display Dependencies from this asset

        tab_inputs = QtGui.QWidget()
        tab_inputs_layout = QtGui.QVBoxLayout(tab_inputs)
        tab_inputs_layout.setContentsMargins(0, 8, 0, 0)
        self._tab_widget.addTab(tab_inputs, "Dependencies")

        # Display Renders from this asset

        tab_renders = QtGui.QWidget()
        tab_renders_layout = QtGui.QVBoxLayout(tab_renders)
        tab_renders_layout.setContentsMargins(0, 8, 0, 0)
        self._tab_widget.addTab(tab_renders, "Asset Renders")

        asset_frame_layout.addWidget(self._tab_widget)

        spacer_global = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum,
                                          QtGui.QSizePolicy.Expanding)
        asset_frame_layout.addItem(spacer_global)

    def initiate_scene_version(self):
        if self.scene_version == None:
            return

        self._asset_name.setText(self.scene_version.getParent().getName())
        self._status.set_status(self.scene_version.getStatus())
        self._asset_version.setText("%03d" % self.scene_version.get('version'))
        # self._thumbnail_widget.update_image(self.scene_version.getThumbanail())
        self.set_owner(self.scene_version.getOwner())
        # self._date.setText(self.scene_version.date_str)
        # self._availability.setText(', '.join(self.scene_version.locations))
        # self.set_asset_type(self.scene_version.asset.connector.asset_type)
        # self._comment.setText(self.scene_version.comment)

        # tuple_editor = self.scene_version.editor()
        # if tuple_editor is not None:
        #     user_edit, date_edit = tuple_editor

        #     editor_lbl = QtGui.QLabel("Last Edit by", self)
        #     editor_lbl.setStyleSheet(self._css_lbl)
        #     self._editor = QtGui.QLabel(self)
        #     self.set_editor(user_edit)
        #     self._editor.setTextFormat(QtCore.Qt.RichText)
        #     self._editor.setTextInteractionFlags(
        #         QtCore.Qt.TextBrowserInteraction)
        #     self._editor.setOpenExternalLinks(True)
        #     date_edit_lbl = QtGui.QLabel("on", self)
        #     date_edit_lbl.setStyleSheet(self._css_lbl)
        #     self._date_edit = QtGui.QLabel(
        #         date_edit.strftime("%A, %d. %B %Y %I:%M%p"), self)
        #     self._date_edit.setStyleSheet(self._css_value)

        #     self._infos_layout.insertRow(4, date_edit_lbl, self._date_edit)
        #     self._infos_layout.insertRow(4, editor_lbl, self._editor)

        # if self.scene_version.asset.locker != None:
        #     self.set_locker()

        self._validate()

    def set_asset_type(self, current_asset_type):
        asset_type_name = current_asset_type
        color = "#282828"
        # for scene_connector in self._scenes_connectors:
        #     if scene_connector.asset_type == current_asset_type:
        #         color = scene_connector.color
        #         asset_type_name = scene_connector.name

        # css_asset_type = """
        #     border-radius: 2px; border: 0px; color: #f0f0f0;
        #     padding: 3px; background: """ + color + """;
        # """
        self._asset_type.setText(asset_type_name)
        # self._asset_type.setStyleSheet(css_asset_type)

    def set_owner(self, owner):
        name = owner.getName()
        email = owner.getEmail()
        thumbnail = owner.getThumbnail()
        if thumbnail == None:
            thumbnail = os.environ["FTRACK_SERVER"] + \
                "/img/userplaceholder.png"
        image = utilities.get_url_file(thumbnail)

        self._owner.setText(
            "<a style='" + self._css_value + "' href='mailto:" + email + "'>" + name + "</a>")
        self._owner.setToolTip("<html><img src=" + image + "/></html>")

    def set_editor(self, editor):
        name = editor.getName()
        email = editor.getEmail()
        thumbnail = editor.getThumbnail()
        if thumbnail == None:
            thumbnail = os.environ["FTRACK_SERVER"] + \
                "/img/userplaceholder.png"
        image = utilities.get_url_file(thumbnail)

        self._editor.setText(
            "<a style='" + self._css_value + "' href='mailto:" + email + "'>" + name + "</a>")
        self._editor.setToolTip("<html><img src=" + image + "/></html>")

    def set_locker(self):
        name = self.scene_version.asset.locker.getName()
        email = self.scene_version.asset.locker.getEmail()
        thumbnail = self.scene_version.asset.locker.getThumbnail()
        if thumbnail == None:
            thumbnail = os.environ["FTRACK_SERVER"] + \
                "/img/userplaceholder.png"
        image = utilities.get_url_file(thumbnail)

        locker_css = "color: #DC2800; text-decoration: none;"
        locker_lbl = QtGui.QLabel("Locked by", self)
        locker_lbl.setStyleSheet(locker_css)

        locker = QtGui.QLabel(self)
        locker.setText(
            "<a style='" + locker_css + "' href='mailto:" + email + "'>" + name + "</a>")
        locker.setTextFormat(QtCore.Qt.RichText)
        locker.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        locker.setOpenExternalLinks(True)
        locker.setToolTip("<html><img src=" + image + "/></html>")
        logging.debug("name: %s" % image)

        self._infos_layout.insertRow(0, locker_lbl, locker)

        self.locked = True

    def set_scene_error(self, error=None):
        if error != None:
            self._scene_error_box.set_error(error)
        else:
            self._scene_error_box.setVisible(False)
        self.error = True

    def set_scene_warning(self, warning):
        self._scene_warning_box.set_warning(warning)

    def initiate_scene_error(self):
        self._scene_error_box.setVisible(False)
        self.error = False

    def initiate_scene_warning(self):
        self._scene_warning_box.setVisible(False)

    def _validate(self):
        errors = []
        warnings = []

        # TODO ---
        try:
            scene_path = self.scene_version.getComponent(name='scene').getFilesystemPath()
            logging.debug(scene_path)

        except Exception as err:
            errors.append(str(err))

        else:
            if scene_path == None:
                error = "This scene doesn't seem to be available in your location. Please"
                "synchronize the script in your location before loading it."
                errors.append(error)

            elif not os.path.isfile(scene_path):
                error = "The scene component exists and is in your location.. However it seems"
                "that its path is incorrect. Did anyone move it or renamed it?"
                errors.append(error)

            elif not scene_path.endswith(".nk"):
                file = os.path.basename(scene_path)
                error = "The scene component exists and is in your location... But this is"
                "not a Nuke script (ending with .nk)<br/>[file: %s]" % file
                errors.append(error)

        if len(errors) > 0:
            self.set_scene_error("<br/><br/>".join(errors))
        else:
            self.initiate_scene_error()

        if len(warnings) > 0:
            self.set_scene_warning("<br/><br/>".join(warnings))
        else:
            self.initiate_scene_warning()
