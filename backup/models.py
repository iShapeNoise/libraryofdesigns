from django.db import models


class Backup(models.Model):
    backup_file = models.FileField(upload_to='lod_db_backup/', blank=False)
