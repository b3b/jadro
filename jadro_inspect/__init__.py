try:
    from jadro_inspect.databases import DATABASES as DROID_DATABASES
except ImportError:
    DROID_DATABASES = {}

INSTALLED_APPS = tuple(['jadro_inspect'] +
                       map(lambda app: '.'.join(('jadro_inspect', 'apps', app)),
                           DROID_DATABASES.keys()))
class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in DROID_DATABASES.keys():
            return model._meta.app_label
        return None
    def allow_syncdb(self, db, model):
        if model._meta.app_label in DROID_DATABASES.keys():
            return False
        return None
