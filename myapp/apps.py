import os
import sys
import threading

from django.apps import AppConfig

BACKUP_INTERVAL_SECONDS = 3600


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        if not self._should_start_scheduler():
            return
        thread = threading.Thread(target=self._backup_loop, daemon=True)
        thread.start()

    def _should_start_scheduler(self):
        prog = sys.argv[0] if sys.argv else ''
        if 'manage.py' in prog:
            if len(sys.argv) < 2:
                return False
            if sys.argv[1] == 'runserver':
                return os.environ.get('RUN_MAIN') == 'true'
            return False
        return True

    def _backup_loop(self):
        import time

        while True:
            time.sleep(BACKUP_INTERVAL_SECONDS)
            try:
                from .backup_utils import run_full_backup
                from .models import DropboxSettings

                settings_obj = DropboxSettings.objects.filter(pk=1).first()
                if settings_obj and settings_obj.is_configured:
                    run_full_backup(settings_obj)
            except Exception:
                pass
