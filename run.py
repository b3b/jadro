#!/usr/bin/env python

import os

TOP_DIR = os.path.dirname(__file__)
su = '/system/bin/su'
python_executable = '/data/data/com.googlecode.pythonforandroid/files/python/bin/python'
run = os.path.join(TOP_DIR, 'tools', 'run.sh')
manage = os.path.join(TOP_DIR, 'manage.py')
cmd = 'runserver --noreload'
os.environ['LC_ALL'] = 'en_US.UTF8'
os.execv(su, ['su', '-c', ' '.join(('sh', run, 'su', 'sh', run, python_executable, manage, cmd))])
