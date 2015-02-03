#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob

modules = glob.glob(os.path.join(os.path.dirname(__file__),"*.py"))
__all__ = [os.path.basename(m)[:-3] for m in modules]

from . import *

__asset_instances = []

def all_assets():
  if len(__asset_instances) == 0:
    import re
    pattern = re.compile("((?!Version|Asset).)*IO$")
    for m in __all__:
      try:
        module = globals()[m]
        for attr in dir(module):
          if re.match(pattern, attr) is not None:
            instance = getattr(module, attr)
            __asset_instances.append(instance)
      except Excpetion as err:
        continue
  return __asset_instances
