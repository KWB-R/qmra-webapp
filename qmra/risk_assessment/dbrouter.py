class DBRouter(object):
    """Default* entities are managed by admins, everything else is for the users"""

    def db_for_read(self, model, **hints):
        if "QMRA" in model.__name__:
            return 'qmra'
        return "default"

    def db_for_write(self, model, **hints):
        if "QMRA" in model.__name__:
            return 'qmra'
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the qmra data (and only this data!) is in its db
        """
        if model_name is not None and "qmra" in model_name:
            return db == "qmra"
        return db == "default"
