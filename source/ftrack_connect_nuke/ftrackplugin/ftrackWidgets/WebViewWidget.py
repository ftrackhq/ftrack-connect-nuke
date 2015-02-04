from PySide import QtCore, QtGui, QtWebKit
from WebView import Ui_WebView
from ftrack_connect_nuke.ftrackplugin import PersistentCookieJar
from ftrack_connect_nuke.ftrackConnector.maincon import HelpFunctions


class WebPage(QtWebKit.QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        print '%s line %d: %s' % (source, line, msg)


class WebViewWidget(QtGui.QWidget):
    def __init__(self, parent, task=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_WebView()
        self.ui.setupUi(self)

        self.webPage = WebPage()
        self.persCookieJar = PersistentCookieJar.PersistentCookieJar(self)
        self.persCookieJar.load()

        # self.webPage.networkAccessManager().setCookieJar(self.persCookieJar)
        proxy = HelpFunctions.getFtrackQNetworkProxy()
        if proxy:
            self.webPage.networkAccessManager().setProxy(proxy)

        self.ui.WebViewView.setPage(self.webPage)

    def sslErrorHandler(self, reply, errorList):
        reply.ignoreSslErrors()
        print ("SSL error ignored")

    def setUrl(self, url):
        self.ui.WebViewView.load(QtCore.QUrl(url))
