from django.apps import AppConfig

class ZooAppConfig(AppConfig):
    name = 'website'

    def ready(self):
        import website.signals  # make sure signals are loaded
