# coding: utf-8
import os
import sys
import inspect

'''
Adds the .floy/floy directory to python's include path.
The 'sys.path....' line must come before the 'from floy import *' one.
'''
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.floy/'))

'''
Importing floy module
'''
import floy

'''
Initializes floy
'''

floy.Core.init(os.path.dirname(__file__))
for method in inspect.getmembers(floy.Tasks):
  if not method[0].startswith('_'):
    setattr(
        __import__(__name__),
        method[0],
        getattr(floy.Tasks, method[0])
    )
