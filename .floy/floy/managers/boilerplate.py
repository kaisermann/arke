from fabric.api import *
from fabric.colors import *
from abc import ABCMeta, abstractmethod


class ManagerBoilerplate(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        if(len(env.tasks) < 2):
            print red('>> Environment was set, but no task was specified.')
            exit(1)

    @abstractmethod
    def setup():
        ''' Must override '''
        pass

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            print red('>> This environment (%s) has no task named "%s"' % (env.name, name))
        return _missing
