from ftrack_connect_nuke.ftrackplugin import ftrackConnector
from PySide import QtGui, QtCore

from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.PlayblastWidget import PlayblastWidget
from ftrack_connect_nuke.ftrackplugin.ftrackWidgets.HeaderWidget import HeaderWidget


class ftrackPlayblastQt(QtGui.QDialog):
    def __init__(self, parent=ftrackConnector.Connector.getMainWindow()):
        super(ftrackPlayblastQt, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)

        self.headerWidget = HeaderWidget(self)
        self.headerWidget.setTitle('Playblast')
        self.verticalMainLayout.addWidget(self.headerWidget)

        self.playblastWidget = PlayblastWidget(self.centralwidget)
        self.verticalMainLayout.addWidget(self.playblastWidget)
        
        self.setInitValues()

        QtCore.QObject.connect(self.playblastWidget.ui.playBlastButton, QtCore.SIGNAL("clicked()"), self.playBlast)
        QtCore.QObject.connect(self.playblastWidget.ui.playLatestButton, QtCore.SIGNAL("clicked()"), self.justPlay)
        QtCore.QObject.connect(self.playblastWidget.ui.fromTimeLineButton, QtCore.SIGNAL("clicked()"), self.setRange)
        QtCore.QObject.connect(self.playblastWidget.ui.setViewButton, QtCore.SIGNAL("clicked()"), self.setView)
        
        self.setObjectName('ftrackPlayblast')
        self.setWindowTitle("ftrackPlayblast")

        self.addCameras()
        
    def setInitValues(self):
        import maya.cmds as mc
        w = mc.getAttr("defaultResolution.width")
        h = mc.getAttr("defaultResolution.height")
        self.playblastWidget.ui.widthEdit.setText(str(w))
        self.playblastWidget.ui.heightEdit.setText(str(h))

    def setView(self):
        import maya.mel as mm
        import maya.cmds as mc
        camera = self.playblastWidget.getCamera()
        stereo = self.playblastWidget.getStereo()

        if stereo == 'multi' and camera != 'Current':
            mm.eval('stereoCameraSwitchToCamera ' + camera + ' ' + mc.getPanel(withFocus=True))
            from maya.app.stereo import stereoCameraCustomPanel
            stereoCameraCustomPanel.switchToCamera(camera, "StereoPanelEditor")
            mm.eval('updateModelPanelBar StereoPanelEditor')
        elif stereo == 'off' and camera != 'Current':
            mm.eval('lookThroughModelPanel ' + camera + ' ' + mc.getPanel(withFocus=True))

    def addCameras(self):
        import maya.cmds as mc
        cameras = mc.ls(type='camera')
        self.playblastWidget.ui.cameraCombo.clear()
        self.playblastWidget.ui.cameraCombo.addItem('Current')
        for cam in cameras:
            parent = mc.listRelatives(cam, parent=True)[0]
            self.playblastWidget.ui.cameraCombo.addItem(parent)

        stereocameras = mc.ls(type='stereoRigCamera')
        for cam in stereocameras:
            currentRow = self.playblastWidget.ui.cameraCombo.count()
            parent = mc.listRelatives(cam, parent=True)[0]
            self.playblastWidget.ui.cameraCombo.addItem(parent)
            self.playblastWidget.ui.cameraCombo.setItemData(currentRow, QtGui.QFont("DejaVu Sans", 10, QtGui.QFont.Bold), QtCore.Qt.FontRole)

        self.playblastWidget.ui.cameraCombo.setCurrentIndex(0)

    def refresh(self):
        self.addCameras()

    def setStereoAnaglyphView(self, cameraName):
        import maya.cmds as mc
        visiblePanels = mc.getPanel(visiblePanels=True)
        modalPanels = mc.getPanel(type='modelPanel')
        usePan = None
        for pan in visiblePanels:
            if pan in modalPanels:
                usePan = pan
                break

        import maya.mel as mel
        mel.eval('stereoCameraSwitchToCamera ' + cameraName + ' ' + usePan)

        from maya.app.stereo import stereoCameraCustomPanel
        stereoCameraCustomPanel.stereoCameraViewCallback("StereoPanelEditor", "{'displayMode': 'anaglyph'}")

    def getOverscans(self):
        import maya.cmds as mc
        cameras = mc.ls(type='camera')
        overScans = []
        for cam in cameras:
            overScans.append((str(cam), mc.getAttr(cam + '.overscan')))
            mc.setAttr(cam + '.overscan', 1.0)
        return overScans

    def setOverscans(self, overscans):
        import maya.cmds as mc
        for scan in overscans:
            mc.setAttr(scan[0] + '.overscan', scan[1])

    def justPlay(self):
        self.playBlast(justPlay=True)

    def playBlast(self, justPlay=None):
        import maya.cmds as mc
        import maya.mel as mm
        import os
        import subprocess
        size = self.playblastWidget.getSize()
        outformat = self.playblastWidget.getFormat()
        stereo = self.playblastWidget.getStereo()

        if self.playblastWidget.getOverscan():
            oldOverscans = self.getOverscans()
            #print oldOverscans

        start, end = self.playblastWidget.getRange()

        # Very fido specific. Needs to be changed
        filename = mc.file(query=True, sn=True, shn=True).split(".")[0]
        path = os.path.join(os.environ['FIDO_SHOW_ROOT'], "shottree", os.environ['FIDO_SEQUENCE'], os.environ['FIDO_SHOT'], "output3d", "preview")

        outfile = os.path.join(path, filename + '')

        if outformat == 'tif':
            typeformat = 'image'
            compression = 'tif'
        else:
            typeformat = 'qt'
            compression = 'jpeg'

        w = self.playblastWidget.getWidth()
        h = self.playblastWidget.getHeight()

        cameraSetups = []
        if stereo == 'multi':
            cameraSetups.append(["stereoCameraView -e -displayMode leftEye StereoPanelEditor", "left"])
            cameraSetups.append(["stereoCameraView -e -displayMode rightEye StereoPanelEditor", "right"])

            if typeformat == 'qt':
                outfilerv = '[ "' + os.path.join(path, filename + '_left.mov') + '" "' + os.path.join(path, filename + '_right.mov') + '" ]'
            elif typeformat == 'image':
                outfilerv = '[ "' + os.path.join(path, filename + '_left.#.tif') + '" "' + os.path.join(path, filename + '_right.#.tif') + '" ]'

        elif stereo == 'off':
            cameraSetups.append(['print "normal"', "single"])

            if typeformat == 'qt':
                outfilerv = "[ " + os.path.join(path, filename + '_single.mov') + " ]"
            elif typeformat == 'image':
                outfilerv = os.path.join(path, filename + '_single.#.tif')

        audio = ''
        if self.playblastWidget.ui.soundCheck.isChecked():
            try:
                gPlayBackSlider = mm.eval('$tmpVar=$gPlayBackSlider')
                audio = mc.timeControl(gPlayBackSlider, query=True, sound=True)
            except:
                pass
            
        showOrn = self.playblastWidget.getOrnaments()

        if not justPlay:
            for k in cameraSetups:
                mc.playblast(format=typeformat, \
                             startTime=start, \
                             endTime=end, \
                             widthHeight=[w, h], \
                             compression=compression, \
                             quality=80, \
                             percent=size, \
                             orn=False, \
                             framePadding=4, \
                             forceOverwrite=True, \
                             offScreen=True, \
                             s=audio, \
                             showOrnaments=showOrn, \
                             viewer=False, \
                             f=outfile, \
                             cameraSetup=k)
        if self.playblastWidget.getOverscan():
            self.setOverscans(oldOverscans)

        cmd = []
        cmd.append(os.environ['RV_PATH'])
        cmd.append(str(outfilerv))
        cmd = " ".join(cmd)
        subprocess.Popen(cmd, shell=True)

    def setRange(self):
        import maya.cmds as mc
        self.playblastWidget.ui.frameStart.setText(str(int(mc.playbackOptions(query=True, min=True))))
        self.playblastWidget.ui.frameEnd.setText(str(int(mc.playbackOptions(query=True, max=True))))


class ftrackPlayblastDialog(ftrackConnector.Dialog):
    def __init__(self):
        super(ftrackPlayblastDialog, self).__init__()
        self.dockName = 'ftrackPlayblast'
        self.gotRefresh = True

    def initGui(self):
        return ftrackPlayblastQt

    @staticmethod
    def accepts():
        return ['']

    @staticmethod
    def category():
        return 'mayatools'
