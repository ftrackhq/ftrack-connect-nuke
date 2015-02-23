# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WebView.ui'
#
# Created: Fri Jun 28 10:27:15 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WebView(object):
    def setupUi(self, WebView):
        WebView.setObjectName("WebView")
        WebView.resize(688, 555)
        self.horizontalLayout = QtGui.QHBoxLayout(WebView)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.WebViewView = QtWebKit.QWebView(WebView)
        font = QtGui.QFont()
        font.setFamily("Anonymous Pro")
        self.WebViewView.setFont(font)
        self.WebViewView.setUrl(QtCore.QUrl("http://feber.se/"))
        self.WebViewView.setObjectName("WebViewView")
        self.horizontalLayout.addWidget(self.WebViewView)

        self.retranslateUi(WebView)
        QtCore.QMetaObject.connectSlotsByName(WebView)

    def retranslateUi(self, WebView):
        WebView.setWindowTitle(QtGui.QApplication.translate("WebView", "Form", None, QtGui.QApplication.UnicodeUTF8))

from PySide import QtWebKit
