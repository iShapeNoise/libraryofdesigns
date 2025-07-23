import subprocess
import psycopg2
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Resets the database (drops, creates, migrates) and creates a superuser.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Tells Django to automatically answer Y to all prompts.',
        )
        parser.add_argument(
            '--no-create-superuser',
            action='store_true',
            help='Skip superuser creation.',
        )

    def handle(self, *args, **options):
        if not options['noinput']:
            confirm = input("Are you sure you want to reset the database? This will erase all data. Type 'yes' to continue: ")
            if confirm != 'yes':
                self.stdout.write(self.style.ERROR('Database reset cancelled.'))
                return

        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT']

        # Connect to the default 'postgres' database to manage privileges and database operations  
        conn = None
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.autocommit = True
            cur = conn.cursor()

            # Grant CREATEDB privilege to the user  
            self.stdout.write(f'Granting CREATEDB privilege to user: {db_user}')
            try:
                cur.execute(f"ALTER USER {db_user} CREATEDB;")
                self.stdout.write(self.style.SUCCESS(f'CREATEDB privilege granted to {db_user}.'))
            except psycopg2.Error as e:
                self.stdout.write(self.style.WARNING(f'Could not grant CREATEDB privilege: {e}. User might already have it or insufficient permissions.'))
            # Drop database  
            self.stdout.write(f'Attempting to drop database: {db_name}')
            try:
                cur.execute(f"DROP DATABASE IF EXISTS {db_name} WITH (FORCE);")
                self.stdout.write(self.style.SUCCESS(f'Database {db_name} dropped successfully (if it existed).'))
            except psycopg2.Error as e:
                self.stdout.write(self.style.WARNING(f'Could not drop database {db_name}: {e}. Attempting to terminate connections and retry.'))
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}'
                      AND pid <> pg_backend_pid();
                """)
                cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
                self.stdout.write(self.style.SUCCESS(f'Database {db_name} dropped after terminating connections.'))
            # Create database  
            self.stdout.write(f'Creating database: {db_name}')
            cur.execute(f"CREATE DATABASE {db_name} WITH OWNER {db_user};")
            self.stdout.write(self.style.SUCCESS(f'Database {db_name} created successfully.'))

            cur.close()

        except psycopg2.Error as e:
            raise CommandError(f'Error connecting to or managing PostgreSQL: {e}')
        finally:
            if conn:
                conn.close()
        # Run migrations  
        self.stdout.write('Running migrations...')
        try:
            subprocess.run(['python', 'manage.py', 'migrate'], check=True)
            self.stdout.write(self.style.SUCCESS('Migrations applied successfully.'))
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Error running migrations: {e}')

        # Create superuser by default (unless --no-create-superuser is specified)  
        if not options['no_create_superuser']:
            self.stdout.write('Creating superuser...')
            username = config('DJANGO_SUPERUSER_USERNAME', default=None)
            email = config('DJANGO_SUPERUSER_EMAIL', default=None)
            password = config('DJANGO_SUPERUSER_PASSWORD', default=None)

            if not all([username, email, password]):
                self.stdout.write(self.style.WARNING(
                    'Superuser creation skipped: Missing username, email, or password. '
                    'Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD in your .env file.'
                ))
            else:
                User = get_user_model()
                try:
                    # Check if user already exists  
                    if User.objects.filter(username=username).exists():
                        self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists.'))
                    else:
                        User.objects.create_superuser(username, email, password)
                        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        else:
            self.stdout.write('Superuser creation skipped due to --no-create-superuser flag.')

        self.stdout.write(self.style.SUCCESS('Database reset process completed.'))
