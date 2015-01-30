import os
from PySide import QtGui, QtCore
from Tasks import Ui_Tasks
import ftrack
from ftrack_connect_nuke import ftrackConnector


class TasksWidget(QtGui.QWidget):
    clickedTaskSignal = QtCore.Signal(str, name='clickedTaskSignal')
    clickedShotTaskSignal = QtCore.Signal(str, name='clickedShotTaskSignal')

    def __init__(self, parent, task=None, onlyCurrentProject=False, enableProjectFiltering=True):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Tasks()
        self.ui.setupUi(self)

        self.ui.tasksTableWidget.verticalHeader().hide()
        self.ui.tasksTableWidget.setColumnCount(5)
        self.ui.tasksTableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.tasksTableWidget.horizontalHeader().resizeSection(1, 80)
        self.ui.tasksTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.ui.tasksTableWidget.horizontalHeader().resizeSection(2, 100)
        self.ui.tasksTableWidget.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)

        self.ui.tasksTableWidget.hideColumn(3)
        self.ui.tasksTableWidget.hideColumn(4)

        self.ui.tasksTableWidget.setHorizontalHeaderLabels(['Task', 'Task Type', 'Status', 'proj', 'state'])

        self.ui.tasksTableWidget.verticalHeader().setDefaultSectionSize(ftrackConnector.Dialog.TABLEROWHEIGHT)

        user = os.environ['LOGNAME']
        ftrackUser = ftrack.User(user)

        ftrackAssignedTasks = ftrackUser.getTasks(includePath=True)

        self.currentId = None
        statusNames = dict()
        statusColors = dict()
        statusStates = dict()
        typeNames = dict()

        self.ui.tasksTableWidget.setRowCount(len(ftrackAssignedTasks))
        for i in range(len(ftrackAssignedTasks)):

            task = ftrackAssignedTasks[i]
            statusid = task.get('statusid')

            typeid = task.get('typeid')
            if typeid in typeNames:
                tasktype = typeNames[typeid]
            else:
                tasktype = task.getType().getName()
                typeNames[typeid] = tasktype

            if statusid in statusNames:
                statusColor = statusColors[statusid]
                statusName = statusNames[statusid]
                statusState = statusStates[statusid]
            else:
                status = task.getStatus()
                statusColor = status.get('color')
                statusName = status.getName()
                statusState = status.getState()
                statusNames[statusid] = statusName
                statusColors[statusid] = statusColor
                statusStates[statusid] = statusState

            parentpath = task.get('path')
            parentId = parentpath[-2].get('id')
            #print parentId
            pathArray = [x.get('name') for x in task.get('path')]
            path = '.'.join(pathArray)

            taskItem = QtGui.QTableWidgetItem(path)
            taskItem.id = task.getId()
            taskItem.parentid = parentId

            statusItem = QtGui.QTableWidgetItem(statusName)
            statusItem.setBackground(QtGui.QBrush(QtGui.QColor(statusColor)))
            statusItem.setForeground(QtGui.QBrush(QtGui.QColor('black')))

            tasktypeItem = QtGui.QTableWidgetItem(tasktype)

            statusStateItem = QtGui.QTableWidgetItem(statusState)

            projectItem = QtGui.QTableWidgetItem(task.getProject().getName())

            self.ui.tasksTableWidget.setItem(i, 0, taskItem)
            self.ui.tasksTableWidget.setItem(i, 1, tasktypeItem)
            self.ui.tasksTableWidget.setItem(i, 2, statusItem)
            self.ui.tasksTableWidget.setItem(i, 3, projectItem)
            self.ui.tasksTableWidget.setItem(i, 4, statusStateItem)

        if onlyCurrentProject:
            self.ui.allProjectsCheckBox.setChecked(False)

        if not enableProjectFiltering:
            self.ui.allProjectsCheckBox.setChecked(True)
            self.ui.allProjectsCheckBox.setEnabled(False)

        self.updateFilters()

    def updateFilters(self):
        projVis = self.showAllProjects(self.ui.allProjectsCheckBox.isChecked())
        stateVis = self.showAllStates(self.ui.showApprovedCheckBox.isChecked())
        for i in range(len(projVis)):
            if projVis[i] and stateVis[i]:
                self.ui.tasksTableWidget.setRowHidden(i, False)
            else:
                self.ui.tasksTableWidget.setRowHidden(i, True)

    def showAllProjects(self, filterStatus):
        projVis = []
        if not filterStatus:
            task = ftrack.Task(os.environ['FTRACK_SHOTID'])
            proj = task.getProject().getName()

            for i in range(self.ui.tasksTableWidget.rowCount()):
                if proj == self.ui.tasksTableWidget.item(i, 3).text():
                    projVis.append(True)
                else:
                    projVis.append(False)
        else:
            for i in range(self.ui.tasksTableWidget.rowCount()):
                projVis.append(True)
        return projVis

    def showAllStates(self, filterStatus):
        stateVis = []
        states = ['NOT_STARTED', 'IN_PROGRESS']
        if not filterStatus:
            for i in range(self.ui.tasksTableWidget.rowCount()):
                if self.ui.tasksTableWidget.item(i, 4).text() in states:
                    stateVis.append(True)
                else:
                    stateVis.append(False)
        else:
            for i in range(self.ui.tasksTableWidget.rowCount()):
                stateVis.append(True)
        return stateVis

    def setCurrentTask(self, modelindex):
        clickedItem = self.ui.tasksTableWidget.item(modelindex.row(), 0)
        self.currentId = clickedItem.parentid
        self.clickedTaskSignal.emit(self.currentId)
        self.clickedShotTaskSignal.emit(clickedItem.id)

    def getCurrentId(self):
        return self.currentId
