import os
from PySide import QtCore, QtGui
from BrowseTasksSmall import Ui_BrowseTasksSmall
from BrowseTasksWidget import BrowseTasksWidget
import ftrack
from ftrack_connect_nuke.ftrackplugin.ftrackConnector import HelpFunctions


class BrowseTasksSmallWidget(QtGui.QWidget):
    clickedIdSignal = QtCore.Signal(str, name='clickedIdSignal')

    def __init__(self, parent, task=None, browseMode='Shot'):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_BrowseTasksSmall()
        self.ui.setupUi(self)
        self.showing = False
        self.parent = parent
        self.ui.cancelButton.hide()

        self.browseMode = browseMode
        self.initPaths()

        self.backgroundLabel = QtGui.QLabel()

        self.ui.browseTasksButton.setText(self.currentpath)

        self.browseTasksWidget = BrowseTasksWidget(parent, startId=self.currentId, browseMode=browseMode)
        self.browseTasksWidget.hide()
        QtCore.QObject.connect(self.browseTasksWidget.ui.BrowseTasksTreeView, \
                               QtCore.SIGNAL("doubleClicked(QModelIndex)"), \
                               self.showHideTree)
        self.topPosition = 0
        self.update()

    def initPaths(self):
        if self.browseMode == 'Shot':
            shot = ftrack.Shot(os.environ['FTRACK_SHOTID'])
            self.currentpath = HelpFunctions.getPath(shot)
            self.currentId = shot.getId()
            self.homeId = os.environ['FTRACK_SHOTID']
        else:
            task = ftrack.Task(os.environ['FTRACK_TASKID'])
            self.currentpath = HelpFunctions.getPath(task)
            self.currentId = task.getId()
            self.homeId = os.environ['FTRACK_TASKID']

    @QtCore.Slot()
    def showHideTree(self):
        if not self.showing:
            self.ui.cancelButton.show()

            windowWidth = self.width()
            windowHeight = self.parent.height()

            ypos = self.topPosition
            heigth = windowHeight - self.height() - self.topPosition

            self.browseTasksWidget.setGeometry(9, \
                                               ypos + 6, \
                                               windowWidth, \
                                               heigth)
            self.browseTasksWidget.show()
            self.browseTasksWidget.raise_()

            self.showing = True
            self.ui.browseTasksButton.setText('Select')
        else:
            self.showing = False
            self.ui.cancelButton.hide()
            self.currentId = self.browseTasksWidget.getCurrentId()
            self.currentpath = self.browseTasksWidget.getCurrentPath()
            self.update()
            self.browseTasksWidget.hide()

    def update(self):
        if self.currentpath:
            self.ui.browseTasksButton.setText(self.currentpath + ' (change)')
            self.clickedIdSignal.emit(self.currentId)
            self.browseTasksWidget.hide()
            #print 'Emit signal'
        else:
            self.ui.browseTasksButton.setText('Select')

    @QtCore.Slot()
    def updateTask(self):
        self.initPaths()
        self.update()

    def setTopPosition(self, topInt):
        self.topPosition = topInt + self.height() - 7  # ui.browseTasksButton.y() + self.ui.browseTasksButton.size().height() + 20

    def setLabelText(self, textLabel):
        self.ui.shotLabel.setText(textLabel)

    def closeTree(self):
        self.showing = False
        self.ui.cancelButton.hide()
        self.browseTasksWidget.hide()
        self.ui.browseTasksButton.setText(self.currentpath + ' (change)')
        
    def goHome(self):
        self.initPaths()
        self.update()
        #self.browseTasksWidget.setStartId(os.environ['FTRACK_SHOTID'])
        #print 'hej'
