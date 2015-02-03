#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class MessageWidget(QtGui.QFrame):
  optional_button_clicked = QtCore.Signal(str)

  def __init__(self, parent=None):
    super(MessageWidget, self).__init__(parent)
    self.setupUI()
    self.setVisible(False)
    self._display_more = False

  def set_error(self, msg, detail=None, button=None, choices=None):
    self._warning_lbl.setText("ERROR")
    self.setStyleSheet("QFrame{ background: #b77; color: #222; }")
    self._header.setStyleSheet("QFrame{ background: #a66; color: #222; }")
    self.set_message(msg, detail, button, choices)

  def set_warning(self, msg, detail=None, button=None, choices=None):
    self._warning_lbl.setText("WARNING")
    self.setStyleSheet("QFrame{ background: #fff5c7; color: #222;}")
    self._header.setStyleSheet("QFrame{ background: #fff6d8; color: #222; }")
    self.set_message(msg, detail, button, choices)

  def set_message(self, msg, detail=None, button=None, choices=None):
    self._warning_header.setText(msg)
    detail_text = detail if detail != None else ""
    self._warning.setText(detail_text)
    self._button_more.setVisible(detail != None)
    self._content.setVisible(self._display_more and detail != None)

    if button is not None:
      self._optional_button.setText(button[0])
      self._optional_button.clicked.connect(self._toggle_optional_button)
      self.optional_button_clicked.connect(button[1])
      self._optional_button.setVisible(True)

      if choices is not None:
        self._optional_combobox.clear()
        self._optional_combobox.addItems(choices)
        self._optional_combobox.setVisible(True)
      else:
        self._optional_combobox.setVisible(False)

    else:
      self._optional_combobox.setVisible(False)
      self._optional_button.setVisible(False)

    self.setVisible(True)

  def toggle_display(self):
    self._display_more = True if not self._content.isVisible() else False
    text_button = "display less" if self._display_more else "display more"
    self._button_more.setText(text_button)
    self._content.setVisible(self._display_more)

  def _toggle_optional_button(self):
    item_chosen = None
    if self._optional_combobox.count() > 0:
      item_chosen = self._optional_combobox.currentText()
    self.optional_button_clicked.emit(item_chosen)

  def setupUI(self):
    self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                         QtGui.QSizePolicy.Maximum))
    main_layout = QtGui.QVBoxLayout(self)
    main_layout.setContentsMargins(0,0,0,0)
    self._header = QtGui.QFrame(self)
    self._header.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                                 QtGui.QSizePolicy.Maximum))
    layout_header = QtGui.QHBoxLayout(self._header)
    layout_header.setContentsMargins(10,10,10,10)
    self._warning_lbl = QtGui.QLabel(self)
    self._warning_lbl.setStyleSheet("font:bold")
    self._warning_lbl.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
    self._warning_lbl.setMaximumWidth(80)
    self._warning_lbl.setMinimumWidth(80)
    layout_header.addWidget(self._warning_lbl)

    self._warning_header = QtGui.QLabel(self)
    self._warning_header.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
    self._warning_header.setWordWrap(True)
    layout_header.addWidget(self._warning_header)

    self._optional_combobox = QtGui.QComboBox(self)
    self._optional_combobox.setMinimumHeight(23)
    self._optional_combobox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                                                            QtGui.QSizePolicy.Fixed))

    optional_button_style = """
      QToolButton { background: #333; color: #FFF;
                    border-radius: 3px; }
      QToolButton:hover { background: #222; color: #FFF;
                          border-radius: 3px; ; }
    """
    self._optional_button = QtGui.QToolButton(self)
    self._optional_button.setMinimumHeight(23)
    self._optional_button.setStyleSheet(optional_button_style)

    self._button_more = QtGui.QToolButton(self)
    button_style = """
      QToolButton { background: none; color: #222;
                    border:0px; text-decoration: none; }
      QToolButton:hover { background: none; color: #333;
                          border:0px; text-decoration: underline; }
    """
    self._button_more.setStyleSheet(button_style)
    self._button_more.setText("display more")
    self._button_more.clicked.connect(self.toggle_display)
    layout_header.addWidget(self._optional_combobox)
    layout_header.addWidget(self._optional_button)
    layout_header.addWidget(self._button_more)
    main_layout.addWidget(self._header)

    self._content = QtGui.QWidget(self)
    layout_content = QtGui.QHBoxLayout(self._content)
    layout_content.setContentsMargins(90,10,10,10)
    self._warning = QtGui.QLabel(self)
    self._warning.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
    self._warning.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
    layout_content.addWidget(self._warning)
    main_layout.addWidget(self._content)
