import os
import sys
from optparse import make_option
from django.core.management.commands.startapp import Command as StartappCommand
from django.template import Template, Context
import jadro_inspect
from jadro_inspect.utils.inspect import sqlite_connection, generate_database_name
from jadro_inspect.management.commands.inspectdb import Command as InspectDBCommand

class Command(StartappCommand):
    option_list = StartappCommand.option_list + (
        make_option('--database_path', action='store', dest='database_path', help='Path to database to introspect.'),
        )
    def handle(self, app_name=None, target=None, **options):
        database_path = options.get('database_path')
        if database_path:
            if not app_name:
                app_name = generate_database_name(database_path)
                if not app_name:
                    sys.stderr.write(self.style.NOTICE("cannot generate name for %r\n" % database_path))                    
            inspect_root = os.path.dirname(jadro_inspect.__file__)
            if not target:
                target = os.path.join(inspect_root, 'apps', app_name)
            if not os.path.exists(target):
                os.mkdir(target)
            super(StartappCommand, self).handle('app', app_name, target, **options)
            # fill models.py with inspectdb command output
            with open(os.path.join(target, 'models.py'), 'w') as models_file:
                models_file.writelines(map(lambda line: '\n'.join((line, '')),
                                           InspectDBCommand()._handle_inspection(
                            sqlite_connection(database_path))))
            try:
                from jadro_inspect.databases import DATABASES
            except ImportError:
                DATABASES = {}
            DATABASES[app_name] = { 'NAME': database_path }
            dblist_template_path = os.path.join(inspect_root, 'conf/databases_template.py')
            with open(dblist_template_path, 'r') as template_file:
                content = Template(template_file.read()).render(Context({
                            'databases': DATABASES}))
            # rewrite databases.py
            with open(os.path.join(inspect_root, 'databases.py'), 'w') as databases_file:
                databases_file.write(content)
        else:
            return super(Command,self).handle(app_name, target, **options)
