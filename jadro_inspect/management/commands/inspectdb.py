import keyword
from optparse import make_option
from django.db.utils import ConnectionHandler
from django.core.management.commands.inspectdb import Command as InspectDBCommand
from django.db import connections

class Command(InspectDBCommand):
    option_list = InspectDBCommand.option_list + (
        make_option('--database_path', action='store', dest='database_path', help='Path to database to introspect.'),
    )

    def handle_inspection(self, options):
        database_path = options.get('database_path')
        if database_path:
            connection = ConnectionHandler({ '_': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': database_path,
                        }}) ['_']
        else:
            connection = connections[options.get('database')]
        return self._handle_inspection(connection, options)

    def _handle_inspection(self, connection, options={}):
        ''' modified version of handle_inspection() from Django core/management/commands/inspectdb.py '''
        table2model = lambda table_name: table_name.title().replace('_', '').replace(' ', '').replace('-', '')

        cursor = connection.cursor()
        yield "# This is an auto-generated Django model module."
        yield "# You'll have to do the following manually to clean this up:"
        yield "#     * Rearrange models' order"
        yield "#     * Make sure each model has one field with primary_key=True"
        yield "# Feel free to rename the models, but don't rename db_table values or field names."
        yield "#"
        yield "# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'"
        yield "# into your database."
        yield ''
        yield 'from %s import models' % self.db_module
        yield ''
        for table_name in connection.introspection.get_table_list(cursor):
            yield 'class %s(models.Model):' % table2model(table_name)
            try:
                relations = connection.introspection.get_relations(cursor, table_name)
            except NotImplementedError:
                relations = {}
            try:
                indexes = connection.introspection.get_indexes(cursor, table_name)
            except NotImplementedError:
                indexes = {}
            for i, row in enumerate(connection.introspection.get_table_description(cursor, table_name)):
                column_name = row[0]
                att_name = column_name.lower()
                comment_notes = [] # Holds Field notes, to be displayed in a Python comment.
                extra_params = {}  # Holds Field parameters such as 'db_column'.

                # If the column name can't be used verbatim as a Python
                # attribute, set the "db_column" for this Field.
                if ' ' in att_name or '-' in att_name or keyword.iskeyword(att_name) or column_name != att_name:
                    extra_params['db_column'] = column_name

                # Add primary_key and unique, if necessary.
                if column_name in indexes:
                    if indexes[column_name]['primary_key']:
                        extra_params['primary_key'] = True
                    elif indexes[column_name]['unique']:
                        extra_params['unique'] = True

                # Modify the field name to make it Python-compatible.
                if ' ' in att_name:
                    att_name = att_name.replace(' ', '_')
                    comment_notes.append('Field renamed to remove spaces.')

                if '-' in att_name:
                    att_name = att_name.replace('-', '_')
                    comment_notes.append('Field renamed to remove dashes.')

                if column_name != att_name:
                    comment_notes.append('Field name made lowercase.')

                if i in relations:
                    rel_to = relations[i][1] == table_name and "'self'" or table2model(relations[i][1])
                    field_type = 'ForeignKey(%s' % rel_to
                    if att_name.endswith('_id'):
                        att_name = att_name[:-3]
                    else:
                        extra_params['db_column'] = column_name
                else:
                    # Calling `get_field_type` to get the field type string and any
                    # additional paramters and notes.
                    field_type, field_params, field_notes = self.get_field_type(connection, table_name, row)
                    extra_params.update(field_params)
                    comment_notes.extend(field_notes)

                    field_type += '('

                if keyword.iskeyword(att_name):
                    att_name += '_field'
                    comment_notes.append('Field renamed because it was a Python reserved word.')

                if att_name[0].isdigit():
                    att_name = 'number_%s' % att_name
                    extra_params['db_column'] = unicode(column_name)
                    comment_notes.append("Field renamed because it wasn't a "
                        "valid Python identifier.")

                # Don't output 'id = meta.AutoField(primary_key=True)', because
                # that's assumed if it doesn't exist.
                if att_name == 'id' and extra_params == {'primary_key': True}:
                    continue

                # Add 'null' and 'blank', if the 'null_ok' flag was present in the
                # table description.
                if row[6]: # If it's NULL...
                    if not 'primary_key' in extra_params: # do not set 'blank' for pk
                        extra_params['blank'] = True
                        if not field_type in ('TextField(', 'CharField('):
                            extra_params['null'] = True

                field_desc = '%s = models.%s' % (att_name, field_type)
                if extra_params:
                    if not field_desc.endswith('('):
                        field_desc += ', '
                    field_desc += ', '.join(['%s=%r' % (k, v) for k, v in extra_params.items()])
                field_desc += ')'
                if comment_notes:
                    field_desc += ' # ' + ' '.join(comment_notes)
                yield '    %s' % field_desc
            for meta_line in self.get_meta(table_name):
                yield meta_line
