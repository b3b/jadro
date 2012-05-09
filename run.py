#!/usr/bin/env python

import os
import android
from collections import defaultdict
from django.core.management import get_commands

droid = android.Android()

class Dialog(object):
    def __init__(self):
        self.commands = get_commands()
    def select(self, title, items):
        droid.dialogCreateAlert(title)
        droid.dialogSetItems(items)
        droid.dialogShow()
        r = droid.dialogGetResponse()
        return (not r.error) and (not 'canceled' in r.result) and items[r.result['item']]
    def select_app(self):
        apps = sorted(set(self.commands.values()))
        return self.select('App', apps)
    def select_command(self, app):
        if not app:
            return
        commands = sorted([k for k, v in self.commands.items() if v == app])
        return self.select('Command', commands)
    def get_options(self, app, cmd):
        if (not app) or (not cmd):
            return
        options = defaultdict(lambda: '', {
                'runserver': '--noreload',
                }) [cmd]
        r = droid.dialogGetInput('Options', '', options)
        return (not r.error) and r.result
    def get_command_to_execute(self):
        app = self.select_app() or ''
        cmd = self.select_command(app) or ''
        options = self.get_options(app, cmd)
        if app and cmd and (not options is None):
            return ' '.join((cmd, options))

TOP_DIR = os.path.dirname(__file__)
su = '/system/bin/su'
python_executable = '/data/data/com.googlecode.pythonforandroid/files/python/bin/python'
run = os.path.join(TOP_DIR, 'tools', 'run.sh')
manage = os.path.join(TOP_DIR, 'manage.py')
os.environ['LC_ALL'] = 'en_US.UTF8'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jadro.settings")
cmd = Dialog().get_command_to_execute()
if cmd:
    os.execv(su, ['su', '-c', ' '.join(('sh', run, 'su', 'sh', run, python_executable, manage, cmd))])
