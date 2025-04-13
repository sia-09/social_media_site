from django.apps import AppConfig

def ready(self):
    import users.signals

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

