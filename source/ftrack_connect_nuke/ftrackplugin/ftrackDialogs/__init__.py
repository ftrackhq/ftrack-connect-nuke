import sys
import os
import imp
import glob
import traceback
cpath = os.path.dirname(os.path.abspath(__file__))
availableDialogs = []
from ftrack_connect_nuke import ftrackConnector

conname = ftrackConnector.Connector.getConnectorName()
if not ftrackConnector.Connector.batch():
    for f in glob.glob(cpath + "/*Dialog.py"):
        modname = os.path.basename(f)[:-3]
        if modname not in ['__init__'] and conname != 'main':
            try:
                exec('from ' + modname + ' import *')
                print 'Imported dialog ' + modname
                availableDialogs.append(modname)
            except:
                print 'Failed to import ' + modname
                traceback.print_exc(file=sys.stdout)
