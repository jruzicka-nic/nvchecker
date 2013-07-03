#!/usr/bin/env python3
# vim:fileencoding=utf-8

import os
import sys
import configparser
import logging
from functools import partial

from pkg_resources import parse_version
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options

from nvchecker.get_version import get_version
from nvchecker import notify

logger = logging.getLogger(__name__)
notifications = []
g_counter = 0
g_oldver = {}
g_curver = {}

define("notify", type=bool,
       help="show desktop notifications when a new version is available")
define("oldverfile", type=str, metavar="FILE",
       help="a text file listing current version info in format 'name: version'")
define("verfile", type=str, metavar="FILE",
       help="write a new version file")

def task_inc():
  global g_counter
  g_counter += 1

def task_dec():
  global g_counter
  g_counter -= 1
  if g_counter == 0:
    IOLoop.instance().stop()
    write_verfile()

def load_config(*files):
  config = configparser.ConfigParser(
    dict_type=dict, allow_no_value=True
  )
  for file in files:
    with open(file) as f:
      config.read_file(f)

  return config

def load_oldverfile(file):
  v = {}
  with open(file) as f:
    for l in f:
      name, ver = [x.strip() for x in l.split(':', 1)]
      v[name] = ver
  return v

def write_verfile():
  if not options.verfile:
    return

  with open(options.verfile, 'w') as f:
    # sort using only alphanums, as done by the sort command, and needed by
    # comm command
    for item in sorted(g_curver.items(), key=lambda i: (''.join(filter(str.isalnum, i[0])), i[1])):
      print('%s: %s' % item, file=f)

def print_version_update(name, version):
  oldver = g_oldver.get(name, None)
  if not oldver or parse_version(oldver) < parse_version(version):
    logger.info('%s: updated version %s', name, version)
    _updated(name, version)
  else:
    logger.info('%s: current version %s', name, version)
  task_dec()

def _updated(name, version):
  g_curver[name] = version

  if options.notify:
    msg = '%s updated to version %s' % (name, version)
    notifications.append(msg)
    notify.update('nvchecker', '\n'.join(notifications))

def get_versions(config):
  task_inc()
  for name in config.sections():
    task_inc()
    get_version(name, config[name], print_version_update)
  task_dec()

def main():
  files = parse_command_line()
  if not files:
    return

  def run_test():
    config = load_config(*files)
    if options.oldverfile:
      g_oldver.update(load_oldverfile(options.oldverfile))
      g_curver.update(g_oldver)
    get_versions(config)

  ioloop = IOLoop.instance()
  ioloop.add_callback(run_test)
  ioloop.start()

if __name__ == '__main__':
  main()