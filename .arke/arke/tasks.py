import core


def setup():
  core.manager.setup()


def checkRequisites():
  core.manager.checkRequisites()


def deploy(branch):
  core.manager.deploy(branch)


def service_restart(name):
  core.manager.service_restart(name)


def service_reload(name):
  core.manager.service_reload(name)


def cleanup_releases():
  core.manager.cleanup_releases(keep)


def fixPermissions(folderPath=0):
  core.manager.fixPermissions(folderPath)


def install():
  core.manager.install()


def reset():
  core.manager.reset()


def git(subtask = ''):
  core.manager.git(subtask)


def wp(subtask = ''):
  core.manager.wp(subtask)


def import_db():
  core.manager.import_db()


def search_replace_db():
  core.manager.search_replace_db()
