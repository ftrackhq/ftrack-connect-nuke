print "Loading ftrack Engine "
import sys
import os
import imp
cpath = os.path.dirname(os.path.abspath(__file__))
modname = 'maincon'


def dependencies_for_freezing():
    import maincon

if hasattr(sys, "frozen"):
    print 'WE are frozen'
    from maincon import *
elif 'TESTCON' in os.environ and os.environ['TESTCON'] == 'TRUE':
    print 'Using test connector'
    from testcon import *
else:
    for f in os.listdir(cpath):
        if f.endswith('.conf'):
            tempmodname = os.path.splitext(f)[0]
            # imp.load_source is used to load a non .py file as a module.
            # This makes it easy to setup settings for each connector
            module_conf = imp.load_source(f, os.path.join(cpath, f))
            if module_conf.conname in sys.executable.lower():
                modname = tempmodname
    print 'Running from ' + str(modname)
    #module_con = __import__('ftrackConnector.connectors.' + modname, \
    #                        fromlist=["something"])
    #Module = module_con.Module
    #print 'Moved class object to main module'
    exec('from ' + modname + ' import *')
    print 'Imported application specific module into global namespace'
