import os
import sys
from PySide import QtCore, QtGui, QtXml
from Applications import Ui_Applications
import Application_rc
import uuid


class LauncherApplication(object):
    def __init__(self, name, location, icon, appid):
        self.name = name
        self.location = location
        self.icon = icon
        self.appid = appid


class ApplicationsWidget(QtGui.QWidget):
    clickedApplicationSignal = QtCore.Signal(str, name='clickedApplicationSignal')

    def __init__(self, parent, task=None, path=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Applications()
        self.ui.setupUi(self)
        self.parent = parent
        
        self.scrollArea = QtGui.QScrollArea(self)
        self.ui.mainLayout.addWidget(self.scrollArea)
        self.ui.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.mainLayout.setSpacing(0)

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        #self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.mainWidget = QtGui.QWidget(self)
        self.scrollArea.setWidget(self.mainWidget)

        self.verticalMainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.verticalMainLayout)

        self.setAutoFillBackground(True)

        self.groups = dict()
        self.appIncludesDict = dict()
        self.appArgumentsDict = dict()
        self.appLocationsDict = dict()
        self.loadingMovies = dict()
        self.appEnvDict = dict()
        self.appMessageLabelsDict = dict()

        self.initApplications(path)

    def getLoadingLabel(self, location):
        return self.loadingMovies[location]

    def getAppMessageLabel(self, appid):
        return self.appMessageLabelsDict[appid]

    def buildAppGui(self):
        for groupname, applist in self.groups.items():
            groupLabel = QtGui.QLabel(self)
            groupLabel.setText(groupname)
            self.verticalMainLayout.addWidget(groupLabel)

            dividerLabel = QtGui.QLabel(self)
            dividerLabel.setObjectName("dividerObject")
            self.verticalMainLayout.addWidget(dividerLabel)

            dividerLabel.setAutoFillBackground(True)
            dividerLabel.setFixedHeight(1)

            groupWidget = QtGui.QWidget(self)
            groupLayout = QtGui.QVBoxLayout(groupWidget)
            groupLayout.setSpacing(1)
            groupLayout.setContentsMargins(5, 5, 5, 5)

            self.verticalMainLayout.addWidget(groupWidget)
            
            for ftapp in applist:
                appItemWidget = QtGui.QWidget(self)
                appItemLayout = QtGui.QHBoxLayout(appItemWidget)
                appItemLayout.setContentsMargins(5, 5, 5, 5)

                appButton = QtGui.QToolButton(self)
                appButton.setFixedSize(250, 30)

                if sys.platform == 'darwin':
                    sysIcon = QtGui.QIcon()
                    sysIcon.addFile(ftapp.icon)
                    appButton.setIcon(sysIcon)
                else:
                    appButton.setIcon(QtGui.QPixmap(ftapp.icon).scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

                appButton.setIconSize(QtCore.QSize(30, 30))
                appButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
                appButton.setAutoRaise(True)
                #appButton.setToolTip(ftapp.name)
                appButton.setText(ftapp.name)
                appButton.setObjectName(ftapp.name)

                QtCore.QObject.connect(appButton, \
                                       QtCore.SIGNAL("clicked()"), \
                                       self.signalMapperApplications, \
                                       QtCore.SLOT("map()"))
                self.signalMapperApplications.setMapping(appButton, ftapp.appid)

                appItemLayout.addWidget(appButton)
                spacerItem = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
                appItemLayout.addItem(spacerItem)

                loadingGifMovie = QtGui.QMovie(":/loading3.gif", QtCore.QByteArray(), self)
                loadingGifMovie.setCacheMode(QtGui.QMovie.CacheAll)
                loadingGifMovie.setSpeed(100)
                loadingGifMovie.setScaledSize(QtCore.QSize(20, 20))

                self.loadingMovies[ftapp.appid] = QtGui.QLabel(self)
                self.loadingMovies[ftapp.appid].setAlignment(QtCore.Qt.AlignCenter)
                self.loadingMovies[ftapp.appid].setMovie(loadingGifMovie)

                appItemLayout.addWidget(self.loadingMovies[ftapp.appid])
                self.appMessageLabelsDict[ftapp.appid] = QtGui.QLabel(self)
                self.appMessageLabelsDict[ftapp.appid].hide()

                appItemLayout.addWidget(self.appMessageLabelsDict[ftapp.appid])

                groupLayout.addWidget(appItemWidget)

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalMainLayout.addItem(spacerItem)

    def parseXml(self, doc):
        groups = doc.elementsByTagName('group')

        for i in range(groups.length()):
            groupElement = groups.item(i).toElement()
            groupId = groupElement.attribute('id')

            if not groupId in self.groups:
                self.groups[groupId] = list()

            applications = groupElement.elementsByTagName('application')
            for j in range(applications.length()):
                applicationElement = applications.item(j).toElement()

                appName = applicationElement.elementsByTagName('name').item(0).toElement().text()
                appIcon = applicationElement.elementsByTagName('icon').item(0).toElement().text()
                appLocation = applicationElement.elementsByTagName('location').item(0).toElement().text()
                appArgument = applicationElement.elementsByTagName('argument').item(0).toElement().text()
                appPlatform = applicationElement.elementsByTagName('platform').item(0).toElement().text()
                
                if appPlatform == '' or appPlatform == sys.platform:
                    appIncludes = applicationElement.elementsByTagName('include')
                    appInclude = []
                    for k in range(appIncludes.length()):
                        appInclude.append(appIncludes.item(k).toElement().text())

                    # extraenv supports a mode keyword which can be 'set',
                    # 'prepend' or 'append'. It defaults to 'set'.
                    appEnvs = applicationElement.elementsByTagName('extraenv')
                    appEnv = []
                    for k in range(appEnvs.length()):
                        extraEnvElement = appEnvs.item(k).toElement()
                        
                        # Specify in the format "mode|key,value". For example:
                        # "prepend|PATH,C:\Program Files\The Foundry\HieroPlayer{0}.{1}v{2}\"
                        appEnv.append(
                            '{0}|{1}'.format(
                                extraEnvElement.attribute(
                                    'mode', defValue='set'
                                ).lower(),
                                extraEnvElement.text()
                            )
                        )

                    replaceHolders = applicationElement.elementsByTagName('replace')
                    ranges = list()
                    for k in range(replaceHolders.length()):
                        splits = replaceHolders.item(k).toElement().text().split('-')
                        if len(splits) == 1:
                            splits.append(splits[0])
                        firstRange = range(int(splits[0]), int(splits[1]) + 1)
                        ranges.append(firstRange)
    
                    import itertools
                    combos = list(itertools.product(*ranges))
                    for combo in combos:
                        appLocationFormated = appLocation.format(*combo)
                        appIconFormated = appIcon.format(*combo)
                        appNameFormated = appName.format(*combo)
    
                        appEnvFormatted = []
                        for env in appEnv:
                            appEnvFormatted.append(env.format(*combo))
    
                        if os.path.isfile(appLocationFormated):
                            appId = str(uuid.uuid4())
                            self.appLocationsDict[appId] = appLocationFormated
                            self.appIncludesDict[appId] = appInclude
                            self.appEnvDict[appId] = appEnvFormatted
                            self.appArgumentsDict[appId] = appArgument
                            self.groups[groupId].append(LauncherApplication(name=appNameFormated, icon=appIconFormated, location=appLocationFormated, appid=appId))

    def initApplications(self, path):
        self.signalMapperApplications = QtCore.QSignalMapper()
        QtCore.QObject.connect(self.signalMapperApplications, \
                               QtCore.SIGNAL("mapped(QString)"), \
                               self.emitApplicationSignal)
        if path:
            fname = path
        else:
            fname = 'apps.xml'

        doc = self.readXmlFromFile(fname)
        if doc:
            self.parseXml(doc)

        if sys.platform == 'darwin':
            os.environ['FTRACK_OVERRIDE_PATH'] = os.environ.get('FTRACK_OVERRIDE_PATH', '')
            from os.path import expanduser
            home = expanduser("~")
            homeftrack = os.path.join(home, '.ftrack')
            if os.path.isdir(homeftrack):
                os.environ['FTRACK_OVERRIDE_PATH'] += os.pathsep + homeftrack

            appsupport = os.path.join('/Library', 'Application Support', 'ftrack')
            if os.path.isdir(appsupport):
                os.environ['FTRACK_OVERRIDE_PATH'] += os.pathsep + appsupport

        if 'FTRACK_OVERRIDE_PATH' in os.environ:
            splitAppsPaths = os.environ['FTRACK_OVERRIDE_PATH'].split(os.pathsep)
            for path in splitAppsPaths:
                appsPath = os.path.join(path, 'apps.xml')
                if os.path.isfile(appsPath):
                    doc = self.readXmlFromFile(appsPath)
                    if doc:
                        self.parseXml(doc)

        self.buildAppGui()

    def readXmlFromFile(self, filePath):
        fileObject = QtCore.QFile(filePath)
        if (not fileObject.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
            QtGui.QMessageBox.warning(self, 'Application', 'Cannot read apps file.')
            return None
        else:
            doc = QtXml.QDomDocument("EnvironmentML")
            if(not doc.setContent(fileObject)):
                fileObject.close()
                QtGui.QMessageBox.warning(self, "Error", "Could not parse xml file.")
            fileObject.close()
            return doc

    @QtCore.Slot(str)
    def emitApplicationSignal(self, appLocation):
        self.clickedApplicationSignal.emit(appLocation)

    def getAppIncludes(self):
        return self.appIncludesDict

    def getAppArguments(self):
        return self.appArgumentsDict

    def getAppLocations(self):
        return self.appLocationsDict

    def getAppEnvs(self):
        return self.appEnvDict
