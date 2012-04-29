class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'jadro_contacts':
            return 'contacts'
        return None
    def allow_syncdb(self, db, model):
        if model._meta.app_label == 'jadro_contacts':
            return False
        return None
