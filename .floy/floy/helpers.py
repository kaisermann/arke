import inspect
import sys
from os.path import join

from fabric.api import *
from fabric.colors import *
from fabric.operations import local


def hideOutput():
  return hide('running', 'output')


def lbash(cmd, considerHidden=False):
  if considerHidden:
    cmd = 'shopt -s dotglob; %s' % cmd
  return local(cmd, False, '/bin/bash')


def whichOption(options, msg='', input_msg='Answer: '):

  if(msg != ''):
    print('\n%s: ' % (msg))

  print '\n0) [Exit script]'
  for i, option in enumerate(options):
    print "%d) %s" % (i + 1, option)
  print ''

  while True:
    returnValue = raw_input(input_msg)

    if(returnValue.isdigit()):
      returnValue = int(returnValue) - 1
      if(returnValue == -1):
        exit(0)
      elif(returnValue >= 0 and returnValue <= len(options) - 1):
        break

  return returnValue


def runCommandList(list, rootPath='', isLocal=False, insertNewline=False):
  newLineCh = '\n'

  if(not insertNewline):
    newLineCh = ''

  for cmdInfo in list:

    if(len(cmdInfo) == 1):
      cmdInfo = ['', cmdInfo[0]]

    cmdPath = join(rootPath, cmdInfo[0])

    print cyan('%s>>> cd ./%s; %s' % (newLineCh, cmdInfo[0], cmdInfo[1]))
    with hide('running'):
      if(isLocal):
        with lcd(cmdPath):
          lbash(cmdInfo[1])
      else:
        with cd(cmdPath):
          if cmdInfo[1].startswith('sudo'):
            sudo(cmdInfo[1])
          else:
            run(cmdInfo[1])

  def search_replace_db(self):
    with hide('everything'), settings(warn_only=True):
      isWpInstallation = lbash('wp core version')

    if(isWpInstallation.return_code == 0):
      while confirm(yellow('Run wp cli search and replace?')):
        oldTerm = raw_input('Old term: ')
        newTerm = raw_input('New term: ')
        lbash('wp search-replace "%s" "%s"' % (oldTerm, newTerm))
    else:
      print red('\n>> Not a WordPress installation.')
