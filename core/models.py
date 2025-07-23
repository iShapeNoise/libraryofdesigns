import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_thumbnails.fields import ThumbnailerImageField
from django.conf import settings


class BackupFile(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Database Backup'
        verbose_name_plural = 'Database Backups'

    def __str__(self):
        return self.filename

    @property
    def file_path(self):
        backup_dir = getattr(settings, 'PG_COPY_BACKUP_PATH', 'lod_db_backup/')
        if not os.path.isabs(backup_dir):
            backup_dir = os.path.join(settings.BASE_DIR, backup_dir)
        return os.path.join(backup_dir, self.filename)

    @property
    def exists(self):
        return os.path.exists(self.file_path)

    def delete_file(self):
        if self.exists:
            os.remove(self.file_path)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, default='No Subject')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


def user_avatar_path(instance, filename):
    """
    Generate upload path for user avatars: user/{user_id}/avatar/{filename}
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename with user ID
    filename = f"avatar.{ext}"
    # Return path: user/{user_id}/avatar/{filename}
    return os.path.join('user', str(instance.user.id), 'avatar', filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = ThumbnailerImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        resize_source=dict(size=(128, 128), crop='smart', quality=95))

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/admin/img/default_avatar.png'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
