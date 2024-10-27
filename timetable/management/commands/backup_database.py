# Create a file: myapp/management/commands/backup_database.py
import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    help = 'Back up the SQLite database to a .sqlite3 backup file'

    def handle(self, *args, **kwargs):
        # Get the database file path
        db_path = settings.DATABASES['default']['NAME']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(
            settings.BASE_DIR, f'backup_{timestamp}.sqlite3'
        )

        # Perform the backup by copying the file
        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f"Backup successful! Backup saved to {backup_path}"))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Backup failed: {e}"))
