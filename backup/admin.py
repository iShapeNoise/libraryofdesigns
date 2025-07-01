from django.contrib import admin
from .models import Backup
from django_object_actions import DjangoObjectActions
from datetime import datetime
from django.conf import settings
import subprocess


class BackupAdmin(DjangoObjectActions, admin.ModelAdmin):
    actions = []

    def create_backup(self, request, queryset):
        backup_path = settings.PG_COPY_BACKUP_PATH
        backup_file = datetime.now()
        backup_file = backup_path + backup_file.strftime("%Y%m%d%H%M%S") + '.sqlc'
        subprocess.call(['/home/lod/.pylod/bin/python3', 'manage.py',
                         'pg_backup', '--file'+backup_file])

    def restore_backup(self, request, queryset):
        pass

    def delete_backup(self, request, queryset):
        pass

    def has_add_permission(self, request, obj=None):
        return False

    changelist_actions = ('create_backup', 
                          'restore_backup',
                          'delete_backup',)


admin.site.register(Backup, BackupAdmin)
