import os
from PySide import QtCore, QtGui
from FileBrowser import Ui_FileBrowser
import glob
import re


class FileBrowserWidget(QtGui.QWidget):
    clickedFileSignal = QtCore.Signal(str, str, str, str)

    def __init__(self, parent, task=None, startPath=''):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_FileBrowser()
        self.ui.setupUi(self)
        
        self.parent = parent
        self.assetType = None

        self.signalMapperAdd = QtCore.QSignalMapper()
        QtCore.QObject.connect(self.signalMapperAdd, \
                               QtCore.SIGNAL("mapped(QString)"), \
                               self.emitAddFileSignal)

        self.startPath = startPath
        self.startPathAdded = False
        self.initFileBrowser()

    def layoutChangedMaybe(self):
        if self.startPathAdded:
            startIndex = self.dirModel.index(self.startPath)
            self.dirSortModel.reset()
            self.dirSortModel.setSourceModel(self.dirModel)
            mappedStartIndex = self.dirSortModel.mapFromSource(startIndex)
            self.ui.dirTreeView.scrollTo(mappedStartIndex, QtGui.QAbstractItemView.PositionAtTop)
            self.ui.dirTreeView.selectionModel().setCurrentIndex(mappedStartIndex, QtGui.QItemSelectionModel.SelectCurrent)
            self.startPathAdded = False
            QtCore.QObject.disconnect(self.dirModel, \
                                      QtCore.SIGNAL("layoutChanged()"), \
                                      self.layoutChangedMaybe)
            self.ui.dirTreeView.expand(mappedStartIndex)
            self.goToPath(self.startPath)

    def checkIfStartPath(self, parent, first, end):
        for i in range(first, end + 1):
            child = parent.child(i, 0)
            path = self.dirModel.filePath(child)
            if self.startPath == path:
                self.startPathAdded = True
                QtCore.QObject.disconnect(self.dirModel, \
                                          QtCore.SIGNAL("rowsInserted(QModelIndex,int,int)"), \
                                          self.checkIfStartPath)

    def initFileBrowser(self):
        self.dirModel = QtGui.QFileSystemModel()

        QtCore.QObject.connect(self.dirModel, \
                               QtCore.SIGNAL("rowsInserted(QModelIndex,int,int)"), \
                               self.checkIfStartPath)
        QtCore.QObject.connect(self.dirModel, QtCore.SIGNAL("layoutChanged()"), \
                               self.layoutChangedMaybe)

        self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.dirModel.setRootPath(QtCore.QDir.rootPath())

        self.dirSortModel = QtGui.QSortFilterProxyModel()
        self.dirSortModel.setSourceModel(self.dirModel)
        self.dirSortModel.setDynamicSortFilter(True)
        self.dirSortModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.dirSortModel.sort(0, QtCore.Qt.AscendingOrder)

        self.ui.dirTreeView.setModel(self.dirSortModel)

        self.ui.dirTreeView.hideColumn(1)
        self.ui.dirTreeView.hideColumn(2)
        self.ui.dirTreeView.hideColumn(3)

        self.ui.fileSequenceTableWidget.setColumnCount(5)
        self.ui.fileSequenceTableWidget.horizontalHeader().setDefaultSectionSize(75)
        self.ui.fileSequenceTableWidget.setColumnWidth(0, 580)
        self.ui.fileSequenceTableWidget.setColumnWidth(4, 40)
        self.ui.fileSequenceTableWidget.hideColumn(3)
        self.ui.fileSequenceTableWidget.verticalHeader().hide()
        self.ui.fileSequenceTableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.ui.fileSequenceTableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.fileSequenceTableWidget.setSortingEnabled(True)
        self.ui.fileSequenceTableWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.fileSequenceTableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)

        self.columnHeaders = ['Filename', 'Start', 'End', 'Padding', 'Add']
        self.ui.fileSequenceTableWidget.setHorizontalHeaderLabels(self.columnHeaders)
        self.ui.fileSequenceTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.goToPath(self.startPath)

    def emitAddFileSignal(self, filename):
        foundItems = self.ui.fileSequenceTableWidget.findItems(filename, QtCore.Qt.MatchStartsWith)
        row = foundItems[0].row()
        curpath = self.ui.pathLineEdit.text()
        frameStart = self.ui.fileSequenceTableWidget.item(row, 1).text()
        frameEnd = self.ui.fileSequenceTableWidget.item(row, 2).text()
        self.clickedFileSignal.emit(curpath, filename, frameStart, frameEnd)

    def updateFileViewer(self, modelIndex):

        newModelIndex = self.dirSortModel.mapToSource(modelIndex)

        self.ui.dirTreeView.expand(modelIndex)
        clickedIndex = newModelIndex
        filePath = self.dirModel.fileInfo(clickedIndex).absoluteFilePath()

        self.ui.pathLineEdit.setText(filePath)

        fileSequences = self.getFileSeqs(filePath)
        allContent = fileSequences

        self.ui.fileSequenceTableWidget.setSortingEnabled(False)
        self.ui.fileSequenceTableWidget.clearContents()

        self.ui.fileSequenceTableWidget.setRowCount(len(allContent))

        for i in range(len(allContent)):
            fileNameItem = QtGui.QTableWidgetItem(allContent[i][0])
            self.ui.fileSequenceTableWidget.setItem(i, 0, fileNameItem)
            firstFrameItem = QtGui.QTableWidgetItem(allContent[i][1])
            self.ui.fileSequenceTableWidget.setItem(i, 1, firstFrameItem)
            lastFrameItem = QtGui.QTableWidgetItem(allContent[i][2])
            self.ui.fileSequenceTableWidget.setItem(i, 2, lastFrameItem)
            paddingItem = QtGui.QTableWidgetItem(str(allContent[i][3]))
            self.ui.fileSequenceTableWidget.setItem(i, 3, paddingItem)
            
            widget = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            widget.setLayout(layout)
            addButton = QtGui.QPushButton('+')
            addButton.setFixedSize(22, 22)
            
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(addButton)
            self.ui.fileSequenceTableWidget.setCellWidget(i, 4, widget)

            QtCore.QObject.connect(addButton, \
                                   QtCore.SIGNAL("clicked()"), \
                                   self.signalMapperAdd, \
                                   QtCore.SLOT("map()"))
            self.signalMapperAdd.setMapping(addButton, allContent[i][0])

        self.ui.fileSequenceTableWidget.setSortingEnabled(True)

    def getFileSeqs(self, dirPath):
        files = glob.glob(dirPath + '/*')
        files = sorted(files)
        result = self.getFileSeqsFromFiles(files)
        return result

    def getFileSeqsFromFiles(self, files):
        paddingDictionary = {}
        firstDictionary = {}
        lastDictionary = {}
        extensionDictionary = {}
        pathDictionary = {}
        
        allowedImageFormats = []
        
        if self.assetType == 'img':
            allowedImageFormats = ['.exr', '.png', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
        elif self.assetType == 'comp':
            allowedImageFormats = ['.nk']
        elif self.assetType == 'scene':
            allowedImageFormats = ['.mb', '.ma']
        elif self.assetType == 'geo':
            allowedImageFormats = ['.mb', '.abc', '.ma']
            
        frameFiles = []

        if not self.ui.sequenceCheckBox.checkState():
            for f in files:
                if os.path.isdir(f) == True:
                    continue
                filePath = os.path.dirname(f)
                fileName, fileExtension = os.path.splitext(f)
                if fileExtension in allowedImageFormats:
                    f = os.path.basename(f)
                    frameFiles.append((f, '#', '#', '#', filePath))
        else:
            for f in files:
                if os.path.isdir(f) == True:
                    continue
                filePath = os.path.dirname(f)
                fileName = os.path.basename(f)
                result = re.split('(\d{3,10})', fileName)
                extension = os.path.splitext(fileName)[1]
                
                if len(result) >= 3:
                    fileHash = "".join(result[:-2])
                    frameNumber = int(result[-2])
                    
                    if extension in allowedImageFormats:
                        currentFirst = firstDictionary.get(fileHash, 1000000000000)
                        firstDictionary[fileHash] = min(frameNumber, currentFirst)

                        currentLast = lastDictionary.get(fileHash, -1)
                        lastDictionary[fileHash] = max(frameNumber, currentLast)

                        extensionDictionary[fileHash] = extension
                        pathDictionary[fileHash] = filePath
                        paddingDictionary[fileHash] = len(result[-2])
                else:
                    if extension in allowedImageFormats:
                        frameFiles.append((fileName, '#', '#', '#', filePath))

            for k, v in firstDictionary.items():
                pad = paddingDictionary[k]
                if v == lastDictionary[k]:
                    frameFiles.append((k + str(v).zfill(pad) + extensionDictionary[k], '#', '#', '#', filePath))
                else:
                    frameFiles.append((k + '#' + extensionDictionary[k], str(v).zfill(pad), str(lastDictionary[k]).zfill(pad), pad, pathDictionary[k]))

        return frameFiles

    def goToPath(self, path):
        if os.path.isdir(path):
            startIndex = self.dirModel.index(path)
            mappedStartIndex = self.dirSortModel.mapFromSource(startIndex)
            self.ui.dirTreeView.setCurrentIndex(mappedStartIndex)
            self.updateFileViewer(mappedStartIndex)
            self.ui.dirTreeView.scrollTo(mappedStartIndex, QtGui.QAbstractItemView.PositionAtTop)
        else:
            print 'Not a directory'

    def editPathPressed(self):
        path = self.ui.pathLineEdit.text()
        self.goToPath(path)

    def toggleShowSequences(self, clickedBool):
        path = self.ui.pathLineEdit.text()
        self.goToPath(path)
        
    def setAssetType(self, assetType):
        self.assetType = assetType

    def refreshPath(self):
        curPath = self.ui.pathLineEdit.text()
        self.goToPath(curPath)