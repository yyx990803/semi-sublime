import os
import platform
import sublime
import sublime_plugin
from subprocess import Popen, PIPE
from os.path import dirname, realpath, join, splitext

IS_OSX = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'
SETTINGS_FILE = 'semi.sublime-settings'
BIN_PATH = join(sublime.packages_path(), dirname(realpath(__file__)), 'semi.js')

settings = sublime.load_settings(SETTINGS_FILE)

def plugin_loaded():
    global settings
    settings = sublime.load_settings(SETTINGS_FILE)

def call_semi(view, data, cmd):
  cdir = get_cdir(view)
  env = None
  if IS_OSX:
    env = os.environ.copy()
    env['PATH'] += ':/usr/local/bin'
  try:
    node_path = settings.get('node_path') or 'node'
    p = Popen([node_path, BIN_PATH, cmd],
      stdout=PIPE, stdin=PIPE, stderr=PIPE,
      cwd=cdir, env=env, shell=IS_WINDOWS)
  except OSError:
    raise Exception('Couldn\'t find Node.js. Make sure it\'s in your $PATH by running `node -v` in your command-line.')
  stdout, stderr = p.communicate(input=data.encode('utf-8'))
  stdout = stdout.decode('utf-8')
  stderr = stderr.decode('utf-8')
  if stderr:
    raise Exception('Error: %s' % stderr)
  else:
    return stdout

def get_cdir(view):
  if view.file_name():
    return dirname(view.file_name())
  else:
    return "/"

class AddSemicolonCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    region = sublime.Region(0, self.view.size())
    buffer = self.view.substr(region)
    formated = call_semi(self.view, buffer, "add")
    if formated:
      self.view.replace(edit, region, formated)

class RemoveSemicolonCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    region = sublime.Region(0, self.view.size())
    buffer = self.view.substr(region)
    formated = call_semi(self.view, get_buffer(self.view), "remove")
    if formated:
      self.view.replace(edit, region, formated)