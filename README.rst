###################
ftrack-connect-nuke
###################

Repository for ftrack connect nuke plugins.

*************
Documentation
*************

Full documentation, including installation and setup guides, can be found at
https://doc.ftrack.com/ftrack-connect-nuke

*********************
Copyright and license
*********************

Copyright (c) 2014 ftrack

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License in the LICENSE.txt file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


Environment Variables:
======================

* FTRACK_SERVER= <ftrack server address>
* FTRACK_APIKEY= <ftrack api key>
* FTRACK_LOCATION_PLUGIN_PATH= <full path to location plugins>
* LOGNAME= <ftrack user>

* NUKE_PATH= ${FTRACK-CONNECT-NUKE}/resource/nuke/nuke_path

# python modules 
* PYTHONPATH=${PYTHONPATH}:~/devel/python-api-v3 # ftrack core lib v3
* PYTHONPATH=${PYTHONPATH}:~/devel/connector/ftrack-connect/source
* PYTHONPATH=${PYTHONPATH}:~/devel/connector/ftrack-connect-foundry/source
* PYTHONPATH=${PYTHONPATH}:~/devel/connector/ftrack-connect-nuke/source
* PYTHONPATH=${PYTHONPATH}:/usr/local/lib/python2.7/dist-packages/ # adding the local os modules available

# waiting for the new connector 
* FTRACK_SHOTID=<ftrack shot id>
* FTRACK_TASKID=<ftrack task id>

# Foundry related envs 
* FOUNDRY_ASSET_LOGGING_SEVERITY=6 
* FOUNDRY_ASSET_API_DEBUG=1 
* FOUNDRY_ASSET_PLUGIN_PATH= ${FTRACK-CONNECT-NUKE}/resource/nuke
