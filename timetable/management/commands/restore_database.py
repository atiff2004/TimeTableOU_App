# Create a file: myapp/management/commands/restore_database.py
import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Restore the SQLite database from a .sqlite3 backup file'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the .sqlite3 backup file')

    def handle(self, *args, **kwargs):
        backup_path = kwargs['backup_file']
        db_path = settings.DATABASES['default']['NAME']

        # Ensure the backup file exists
        if not os.path.exists(backup_path):
            self.stdout.write(self.style.ERROR("Backup file does not exist"))
            return

        # Perform the restore by replacing the database file
        try:
            shutil.copy2(backup_path, db_path)
            self.stdout.write(self.style.SUCCESS("Database restored successfully"))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Restore failed: {e}"))
