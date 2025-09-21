from django.apps import AppConfig
import os


class StoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stories'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        import sys
        if any(cmd in sys.argv for cmd in ['migrate', 'test', 'collectstatic', 'makemigrations']):
            return

        try:
            from . import scheduler
            scheduler.start_scheduler()
        except Exception as e:
            print("Помилка запуску планувальника: {}".format(e))