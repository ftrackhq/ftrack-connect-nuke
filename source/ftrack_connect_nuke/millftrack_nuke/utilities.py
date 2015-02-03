#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import os, re

from pytz import timezone
import datetime

from FnAssetAPI import logging

MY_LOCATION = os.environ.get("MILL_JOB_LOCATION", 'LONDON')

LOC_TIMEZONES = dict( LONDON= timezone('Europe/London'),
                      LA= timezone('America/Los_Angeles'),
                      CHICAGO= timezone('America/Chicago'),
                      NY= timezone('America/New_York') )

# The server is in NY so the assets are in NY time and must be converted
SERVER_TIME = LOC_TIMEZONES["NY"]


def current_time():
  return datetime.datetime.now(LOC_TIMEZONES[MY_LOCATION])


def date_with_tz(date, local=False):
  tz = LOC_TIMEZONES[MY_LOCATION] if local else SERVER_TIME
  date = date.replace(tzinfo=tz)
  if not local and MY_LOCATION != "NY":
    date = date.astimezone(LOC_TIMEZONES[MY_LOCATION])
  return date


def dir_temp():
  ''' Return dir temp location
  '''
  dir_temp = os.getenv("NUKE_TEMP_DIR", os.path.join(os.sep,"var","tmp","nuke"))
  if not os.path.isdir(dir_temp):
    os.mkdir(dir_temp)
  logging.debug(dir_temp)
  return dir_temp


def get_url_file(url, overwrite=False):
  ''' Copy an url file into the nuke tmp if necessary
  '''
  logging.debug(url)
  file_name = url.rsplit("/",1)[-1]
  if re.search("^[a-zA-Z0-9\._-]+\?[a-zA-Z0-9\._-]+\=[a-zA-Z0-9\._-]+(\&[a-zA-Z0-9\._-]+\=[a-zA-Z0-9\._-]+)*$", file_name):
    file_name = "_".join(re.findall("(?<=\=)[a-zA-Z0-9\._-]+", file_name.split("?",1)[-1]))
  else:
    file_name = "".join([l for l in file_name.split("?",1)[-1] if l.isalnum() or l in [".","-","_"]])

  file_path = os.path.join(dir_temp(), file_name)

  if not overwrite and os.path.isfile(file_path):
    return file_path

  ftrackProxy = os.getenv("FTRACK_PROXY", "")
  ftrackServer = os.getenv("FTRACK_SERVER", "")

  if ftrackProxy != "":
    httpHandle = "https" if ftrackServer.startswith('https') else "http"
    proxy = urllib2.ProxyHandler({httpHandle: ftrackProxy})
    opener = urllib2.build_opener(proxy)
    response = opener.open(url)
    html = response.read()
  else:
    response = urllib2.urlopen(url)
    html = response.read()

  output = open(file_path, 'wb')
  output.write(html)
  output.close()
  logging.debug(file_path)
  return file_path


def get_pixmap_file(name_file, pixmap, overwrite=False):
  ''' Save a pixmap into the nuke temp if necessary
  '''
  file_path = os.path.join(dir_temp(), name_file + ".png")
  if not overwrite and os.path.isfile(file_path):
    return file_path

  pixmap.save(file_path, format="PNG", quality=100)
  logging.debug(file_path)
  return file_path

