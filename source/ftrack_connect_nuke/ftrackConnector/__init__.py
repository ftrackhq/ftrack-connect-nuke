# print "Loading ftrack Engine "
# import sys
# import os
# import imp
# import FnAssetAPI

# cpath = os.path.dirname(os.path.abspath(__file__))
# modname = 'maincon'


# for f in os.listdir(cpath):
#     if f.endswith('.conf'):
#         tempmodname = os.path.splitext(f)[0]
#         # imp.load_source is used to load a non .py file as a module.
#         # This makes it easy to setup settings for each connector
#         module_conf = imp.load_source(f, os.path.join(cpath, f))
#         if module_conf.conname in sys.executable.lower():
#             modname = tempmodname

# FnAssetAPI.logging.info('Running from ' + str(modname))
# exec('from ' + modname + ' import *')
# FnAssetAPI.logging.info('Imported application specific module into global namespace')

from nukecon import Dialog, Connector