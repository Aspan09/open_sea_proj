from django.apps import AppConfig


class MammothsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mammoths'

    def ready(self):
        import mammoths.signals