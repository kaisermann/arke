from __future__ import absolute_import, unicode_literals, with_statement

import os
import random
import shutil
import tempfile
import time
from os.path import join as j
from os.path import isdir, isfile, relpath

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

import floy
from floy.helpers import *
from floy.managers.boilerplate import ManagerBoilerplate

projectTypes = ['HTML', 'PHP', 'Simple WordPress', 'Bedrock WordPress']
projectTypeValues = ['html', 'php', 'simple-wordpress', 'bedrock-wordpress']


class LocalManager(ManagerBoilerplate):

  def setup(self):
    if not confirm('Setup a new project at "%s"?' % floy.Core.paths['base']):
      exit(0)

    projectType = projectTypeValues[
        whichOption(projectTypes,
                    'Which kind of project it is?',
                    'Project Type: '
                    )
    ]

    targetDir = floy.Core.paths['base']

    with hide('running'):
      with lcd(targetDir):
        if(projectType == 'html' or projectType == 'php'):  # HTML OR PHP
          print yellow('\n>> Downloading phase')
          lbash(
              'git clone --depth=1 --branch=master git@github.com:kaisermann/phase.git phase;')
          lbash('rm -rf phase/{.git,.gitignore,readme.md}; mv phase/* .; rm -rf phase;', True)
          print green('>> Done downloading phase')

          print yellow('\n>> Creating basic file structure')
          if(projectType == 'php'):
            lbash('touch index.php')
            lbash('mkdir -p src views/partials')
          else:
            lbash('touch index.html')
          print green('>> Done creating basic file structure')

        elif(projectType == 'simple-wordpress'):  # WordPress
          print yellow('\n>> Downloading WordPress')
          lbash(
              'curl --silent https://wordpress.org/latest.tar.gz | tar xz; mv wordpress/* .;', True)
          lbash('rm -rf license.txt readme.html wp-config*.php wordpress/;')
          print green('>> Done downloading WordPress')

          print yellow('\n>> Downloading sepha')
          lbash(
              'git clone --depth=1 --branch=master git@github.com:kaisermann/sepha.git sepha;')
          lbash('rm -rf sepha/.git; mv sepha wp-content/themes/;', True)
          print green('>> Done downloading sepha')

        elif(projectType == 'bedrock-wordpress'):  # Bedrock
          print yellow('\n>> Downloading Bedrock')
          lbash(
              'git clone --depth=1 --branch=master git@github.com:roots/bedrock.git bedrock;')
          print green('>> Done downloading Bedrock')

          print yellow('\n>> Downloading sepha')
          lbash(
              'git clone --depth=1 --branch=master git@github.com:kaisermann/sepha.git sepha;')
          print green('>> Done downloading sepha')

          print yellow('\n>> Arranging project files')
          lbash(
              'rm -rf bedrock/{.git,.gitignore,.github,*.md}; mv bedrock/* ./; rm -rf bedrock;', True)
          lbash('rm -rf sepha/.git; mv sepha web/app/themes/;', True)
          print green('>> Done arranging project files')

      print yellow('\n>> Updating floy.json')
      overwriteJson = True
      jsonFileExists = isfile(j(floy.Core.paths['base'], 'floy.json'))

      if(jsonFileExists):
        overwriteJson = confirm(
            '"floy.json" already exists. Overwrite it with the respective project type template?')

      with lcd(floy.Core.paths['base']):
        if(overwriteJson):
          if(jsonFileExists and confirm('Backup the current "floy.json"?')):
            lbash('cp floy.json floy.json.bk')
          lbash('cp -f %s/templates/floy/%s.json floy.json' %
                (floy.Core.paths['auxFiles'], projectType))
          floy.Core.loadOptions()

      floy.Core.options['project']['type'] = projectType
      floy.Core.saveOptions()
      print green('>> Done updating floy.json')

      print ''
      confirm('Should configure the project git repository?') and self.git('setup')

      self.install()

  def install(self):
    print yellow('\n>> Executing local installation process')
    projectType = floy.Core.options['project']['type']

    runCommandList(floy.Core.options['project']['cmds']['install'],
                   floy.Core.paths['base'],
                   True,
                   True)

    with lcd(floy.Core.paths['base']), hide('running', 'output'):
      if(projectType == 'simple-wordpress' and confirm('Configure wp-config.php?')):
        self.wp('configure', 'wp-config.php')

      elif(projectType == 'bedrock-wordpress' and confirm('Configure .env?')):
        self.wp('configure', '.env')

    print green('>> Done executing local installation process')

  def wp(self, subtask='', confFileName=None):

    if(subtask == ''):
      print red('Missing subtask')
      exit(1)

    print yellow('\n>> Executing git "%s" subtask' % subtask)

    if(subtask == 'configure'):

      fileToTemplateDict = {
          'wp-config.php': 'wp-config.php',
          '.env': 'dotenv'
      }

      print yellow('\n>> Configuring "%s"' % confFileName)
      fields = [
          'DB_NAME',
          'DB_USER',
          'DB_PASSWORD',
          'DB_HOST',
          'WP_PREFIX',
          'WP_HOME',
          'ENVIRONMENT'
      ]

      if not confFileName:
        fileNames = ['wp-config.php', '.env']
        confFileName = fileNames[
            whichOption(fileNames,
                        'Which kind of configuration file?',
                        'Configuration filetype: '
                        )
        ]

      templateName = fileToTemplateDict[confFileName]

      with lcd(floy.Core.paths['base']), hide('running'):
        if isfile(j(floy.Core.paths['base'], confFileName)) and confirm('Backup old configuration file?'):
          lbash('mv %s %s.bak' % (templateName, confFileName))

        lbash('cp -rf %s/templates/wp/%s %s' %
              (floy.Core.paths['auxFiles'], templateName, confFileName))

        for field in fields:
          if(field == 'ENVIRONMENT'):
            fieldVal = 'DEVELOPMENT'
          else:
            fieldVal = raw_input('Insert field %s: ' % field)

            if(field == 'WP_PREFIX'):
              fieldVal = fieldVal or 'wp_'

          lbash("sed -i \'\' -e\'s/{{ %s }}/%s/\' %s" %
                (field, fieldVal, confFileName))

      if(confFileName == '.env'):
        with hide('everything'), settings(warn_only=True):
          ret = lbash('wp dotenv salts regenerate')
          if(ret.return_code == 0):
            print cyan('>>> Generating salts')
      print green('>> Done configuring "%s"' % confFileName)
    else:
      print red('Invalid subtask')
      exit(1)

    print green('>> Done executing git "%s" subtask' % subtask)

  def git(self, subtask='', recursiveLevel=0):
    returnValue = None

    if(subtask == ''):
      print red('Missing subtask')
      exit(1)

    print yellow('\n>> Executing git "%s" subtask' % subtask)
    if(subtask == 'setup'):
      print red('Do not do this with an already commited project. The ".git" folder will be DELETED.')
      repoUrl = floy.Core.options['project']['repo']

      if not confirm('Use the url from "floy.json" (%s)?' % repoUrl):
        repoUrl = raw_input('\nType the repository origin url: ')
        print cyan('\n>>> Updating repository origin url on floy.json')
        floy.Core.options['project']['repo'] = repoUrl
        floy.Core.saveOptions()

      with lcd(floy.Core.paths['base']), hideOutput():
        print cyan('>>> Deleting old .git folder')
        lbash('rm -rf .git/')
        print cyan('>>> Initializing new git with origin as "%s"' % repoUrl)
        lbash('git init; git remote add origin %s' % repoUrl)
    else:
      print red('Invalid subtask')
      exit(1)

    endlineChar = ''
    if(recursiveLevel > 0):
      endlineChar = '\n'

    print green('>> Done executing git "%s" subtask%s' % (subtask, endlineChar))
    return returnValue

  def reset(self):
    if confirm('Should delete everything but "floy" files?'):
      print '\nType "0" to cancel\n'
      randomSum = -1
      randomNumber1 = randomNumber2 = 0
      while randomSum != (randomNumber1 + randomNumber2) and randomSum != 0:
        randomNumber1 = random.randint(1, 9)
        randomNumber2 = random.randint(1, 9)
        try:
          randomSum = int(raw_input('How much is %d + %d = ' % (randomNumber1, randomNumber2)))
        except:
          randomSum = -1

      if(randomSum == 0):
        exit(0)

      files = [
          '.floy',
          'floy.json',
          'fabfile.py',
          '.git',
          '.gitignore',
          '.editorconfig',
          'readme.md'
      ]
      print yellow('\n>> Deleting non-floy files and folders')
      with lcd(floy.Core.paths['base']), hide('everything'), settings(warn_only=True):
        tmpDir = tempfile.mkdtemp()
        for f in files:
          lbash('cp -rf %s %s/' % (f, tmpDir))
        lbash('ls -A1 | xargs rm -rf')
        for f in files:
          lbash('cp -rf %s/%s ./' % (tmpDir, f))
        shutil.rmtree(tmpDir)
      print green('>> Done resetting')

  def import_db(self):
    if(env.host == None):
      print red('Missing -H {host} flag.\nUsage: "fab local import_db -H hostToImportFrom" ')
      exit(1)
    print yellow('\n>> Starting DB import process from host(s): %s' % env.host)

    dbuser = raw_input('Database user: ')
    dbname = raw_input('Database name: ')
    print ''

    dumpname = '%s_%s.sql' % (dbname, time.strftime('%Y%m%d-%H%M%S'))

    remoteDir = '~/.dumps'
    localDir = '%s/.dumps' % floy.Core.paths['base']

    remoteDump = '%s/%s' % (remoteDir, dumpname)
    localDump = '%s/%s' % (localDir, dumpname)

    with hide('running'):
      print cyan('>>> Creating REMOTE folder: "%s"' % remoteDir)
      run('mkdir -p %s' % remoteDir)

      print cyan('>>> Creating LOCAL folder: "%s"' % remoteDir)
      lbash('mkdir -p %s' % localDir)

      print cyan('>>> Dumping "%s" onto REMOTE "%s"' % (dbname, remoteDir))
      run('mysqldump -u %s -p %s > %s' % (dbuser, dbname, remoteDump))

      print cyan('>>> Transfering dump file onto LOCAL "%s"' % localDir)
      get(remoteDir, localDump)

      print green('>> Done dumping to "%s"' % localDir)

      print ''
      if confirm('Import last dump to a local database?'):
        dbuser = raw_input('Local Database user: ')
        dbpass = raw_input('Local Database password: ')
        dbname = raw_input('Local Database name: ')
        with hide('warnings', 'output'), settings(warn_only=True):
          lbash('mysql -u %s -p%s -e "DROP DATABASE IF EXISTS %s";' %
                (dbuser, dbpass, dbname))
          lbash('mysql -u %s -p%s -e "CREATE DATABASE %s";' %
                (dbuser, dbpass, dbname))
          lbash('mysql -u %s -p%s %s < %s;' %
                (dbuser, dbpass, dbname, localDump))
        print green('>> Done importing to a local database')
