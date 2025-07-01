from django.core.management.base import BaseCommand
from ..models import Backup


class BackupCommand(BaseCommand):
    help = 'Creates an backup of postgresql database'

    def handle(self, *args, **options):
        self.stdout.write('Hello')
        
