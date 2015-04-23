import os, platform, re
import sublime
import sublime_plugin
from subprocess import Popen, PIPE
from os.path import dirname, realpath, join, splitext

IS_OSX = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'
SETTINGS_FILE = 'semi.sublime-settings'
PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))
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
  except OSError as err:
    node_not_found = bool(re.search('node', str(err)))
    if node_not_found:
      msg = 'Couldn\'t find Node.js. Make sure it\'s in your $PATH. Or, do you want to manually set the path to node?'
      if sublime.ok_cancel_dialog(msg):
        view.window().open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

  stdout, stderr = p.communicate(input=data.encode('utf-8'))
  stdout = stdout.decode('utf-8')
  stderr = stderr.decode('utf-8')
  if stderr:
    sublime.error_message(stderr)
  else:
    return stdout

def get_cdir(view):
  if view.file_name():
    return dirname(view.file_name())
  else:
    return "/"

def not_supported(view):
  file_path = view.file_name()
  view_settings = view.settings()
  has_js_or_html_extension = file_path != None and bool(re.search(r'\.(jsm?|html?)$', file_path))
  has_js_or_html_syntax = bool(re.search(r'JavaScript|HTML', view_settings.get("syntax"), re.I))
  has_json_syntax = bool(re.search("JSON", view_settings.get("syntax"), re.I))
  return has_json_syntax or (not has_js_or_html_extension and not has_js_or_html_syntax)

class AddSemicolonsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if not_supported(self.view):
      return
    region = sublime.Region(0, self.view.size())
    buffer = self.view.substr(region)
    formated = call_semi(self.view, buffer, "add")
    if formated:
      self.view.replace(edit, region, formated)

class RemoveSemicolonsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if not_supported(self.view):
      return
    region = sublime.Region(0, self.view.size())
    buffer = self.view.substr(region)
    formated = call_semi(self.view, buffer, "remove")
    if formated:
      self.view.replace(edit, region, formated)

class SemiOpenSettingsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.window().open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

class SemiOpenKeymapCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    platform = {
      "windows": "Windows",
      "linux": "Linux",
      "osx": "OSX"
    }.get(sublime.platform())
    self.view.window().open_file(PLUGIN_FOLDER + "/Default (" + platform + ").sublime-keymap")