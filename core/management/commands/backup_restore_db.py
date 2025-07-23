import os
import subprocess
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from decouple import config
from core.models import BackupFile

class Command(BaseCommand):
    help = 'Backup and restore PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['backup', 'restore', 'list'],
            help='Action to perform: backup, restore, or list'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Backup file path (for restore) or custom backup filename'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'backup':
            self.create_backup(options.get('file'))
        elif action == 'restore':
            if not options.get('file'):
                raise CommandError('--file argument is required for restore operation')
            self.restore_backup(options['file'])
        elif action == 'list':
            self.list_backups()

    def get_db_config(self):
        """Get database configuration from settings"""
        db_settings = settings.DATABASES['default']
        return {
            'name': db_settings['NAME'],
            'user': db_settings['USER'],
            'password': db_settings['PASSWORD'],
            'host': db_settings['HOST'],
            'port': db_settings['PORT']
        }

    def get_backup_dir(self):
        """Get backup directory path"""
        backup_dir = getattr(settings, 'PG_COPY_BACKUP_PATH', 'lod_db_backup/')
        if not os.path.isabs(backup_dir):
            backup_dir = os.path.join(settings.BASE_DIR, backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def create_backup(self, custom_filename=None):
        """Create database backup using pg_dump"""
        db_config = self.get_db_config()
        backup_dir = self.get_backup_dir()

        if custom_filename:
            filename = custom_filename
            if not filename.endswith('.sql'):
                filename += '.sql'
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{db_config['name']}_backup_{timestamp}.sql"

        backup_path = os.path.join(backup_dir, filename)

        cmd = [
            'pg_dump',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', db_config['name'],
            '-f', backup_path,
            '--verbose',
            '--no-password'
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        try:
            self.stdout.write(f'Creating backup: {backup_path}')
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                file_size = os.path.getsize(backup_path)
                BackupFile.objects.create(filename=filename, file_size=file_size)
                self.stdout.write(
                    self.style.SUCCESS(f'Backup created successfully: {backup_path}')
                )
            else:
                raise CommandError(f'Backup failed: {result.stderr}')

        except Exception as e:
            raise CommandError(f'Backup failed: {str(e)}')

    def restore_backup(self, backup_file):
        """Restore database from backup file"""
        db_config = self.get_db_config()
        backup_dir = self.get_backup_dir()

        if not os.path.isabs(backup_file):
            backup_path = os.path.join(backup_dir, backup_file)
        else:
            backup_path = backup_file

        if not os.path.exists(backup_path):
            raise CommandError(f'Backup file not found: {backup_path}')

        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', db_config['name'],
            '-f', backup_path,
            '--quiet'
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        try:
            self.stdout.write(f'Restoring from backup: {backup_path}')
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('Database restored successfully'))
            else:
                raise CommandError(f'Restore failed: {result.stderr}')

        except Exception as e:
            raise CommandError(f'Restore failed: {str(e)}')

    def list_backups(self):
        """List available backup files"""
        backup_dir = self.get_backup_dir()

        if not os.path.exists(backup_dir):
            self.stdout.write('No backup directory found.')
            return

        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]

        if not backup_files:
            self.stdout.write('No backup files found.')
            return

        self.stdout.write(f'Available backups in {backup_dir}:')
        backup_files.sort(reverse=True)

        for backup_file in backup_files:
            file_path = os.path.join(backup_dir, backup_file)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

            self.stdout.write(
                f'  {backup_file} ({file_size} bytes, {mod_time.strftime("%Y-%m-%d %H:%M:%S")})'
            )
