import sys
from itertools import chain
from django.core.management.base import BaseCommand, CommandError
from jadro_inspect.utils.inspect import find_databases

class Command(BaseCommand):
    help = 'find sqlite databases'
    args = '<search_path search_path ...>'
    
    def handle(self, *args, **options):
        for db in chain(*map(find_databases, args or ['/data/data'])):
            sys.stdout.write("%s\n" % db)
            sys.stdout.flush()
