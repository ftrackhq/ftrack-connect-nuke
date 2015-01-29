# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import functools

import FnAssetAPI
from FnAssetAPI.ui.toolkit import QtGui
from ftrack_connect_foundry.ui import delegate


class Delegate(delegate.Delegate):
    def __init__(self, bridge):
        super(Delegate, self).__init__(bridge)

        self.moduleName =  ".".join(__name__.split(".")[:-1])

    def populate_ftrack(self):

        import nuke
        from legacy import *



    def populateUI(self, uiElement, specification, context):
        super(Delegate, self).populateUI(uiElement, specification, context)

        host = FnAssetAPI.SessionManager.currentSession().getHost()

        if host and host.getIdentifier() == 'uk.co.foundry.nuke': 
            self.populate_ftrack()


            # fileMenu.addCommand("Save Comp", "os.environ",index=startingIndex)
            # versionUpMethod = "%s.utils._script_version_all_up()" % moduleName
            # versionUpTitle = "Save New &Version"
            # item = fileMenu.addCommand(versionUpTitle, versionUpMethod)
