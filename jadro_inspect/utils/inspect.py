import os
import sqlite3
from itertools import ifilter, imap
from fnmatch import fnmatch
from django.db.utils import ConnectionHandler

def is_database_file(db_path):
    if not fnmatch(db_path, "*.db"):
        return False
    try:
        cursor = sqlite3.connect(db_path).cursor()
        cursor.execute('SELECT * FROM sqlite_master')
        cursor.close()
    except sqlite3.DatabaseError:
        return False
    return True

def find_databases(dirpath):
    for d, dirs, files in os.walk(dirpath):
        for f in ifilter(is_database_file,
                         imap(lambda f: os.path.join(d, f), files)):
            yield f

def generate_database_name(db_path):
    p = db_path.split('/')
    db_name, ext = os.path.splitext(p[-1])
    try:
        db_name = '.'.join((
                p[-3] if p[-2] == 'databases' else p[-2],
                db_name))
    except IndexError:
        pass
    db_name = db_name.replace('.', '_')
    db_name = filter(lambda  c: c.isalnum() or c in ('_',), db_name)
    return db_name

def sqlite_connection(database_path):
    return ConnectionHandler({ '_': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': database_path,
                }}) ['_']
