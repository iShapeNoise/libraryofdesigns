import os
import subprocess
import datetime
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib import messages
from django.conf import settings
from django.utils.html import format_html
from decouple import config
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
from .models import UserProfile, ContactMessage, BackupFile


# Create the inline for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('avatar', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;" />', obj.avatar.url)
        return "No avatar uploaded"
    avatar_preview.short_description = 'Current Avatar'


# Custom fieldsets to reorganize the admin layout  
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    # Reorganize fieldsets to group related information  
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'avatar_thumbnail')

    def avatar_thumbnail(self, obj):
        try:
            if obj.profile.avatar:
                return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.profile.avatar.url)
            return "No avatar"
        except UserProfile.DoesNotExist:
            return "No profile"
    avatar_thumbnail.short_description = 'Avatar'


# Apply the custom admin  
UserAdmin.inlines = UserAdmin.inlines + (UserProfileInline,)
UserAdmin.list_display = UserAdmin.list_display + ('avatar_thumbnail',)
UserAdmin.avatar_thumbnail = CustomUserAdmin.avatar_thumbnail


@admin.register(BackupFile)
class BackupFileAdmin(admin.ModelAdmin):
    change_list_template = 'admin/backup_list.html'
    list_display = ['filename', 'created_at', 'file_size_display', 'exists', 'action_buttons']
    list_filter = ['created_at']
    readonly_fields = ['filename', 'created_at', 'file_size']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create-backup/', self.admin_site.admin_view(self.create_backup_view), name='core_backupfile_create'),
            path('restore-backup/<int:backup_id>/', self.admin_site.admin_view(self.restore_backup_view), name='core_backupfile_restore'),
            path('delete-backup/<int:backup_id>/', self.admin_site.admin_view(self.delete_backup_view), name='core_backupfile_delete'),
            path('refresh-backups/', self.admin_site.admin_view(self.refresh_backups_view), name='core_backupfile_refresh'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        self.refresh_backup_list()
        return super().changelist_view(request, extra_context)

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}" onclick="return confirm(\'Are you sure you want to restore from this backup? All current data will be lost!\')">Restore</a>&nbsp;'
            '<a class="button" href="{}" onclick="return confirm(\'Are you sure you want to delete this backup?\')">Delete</a>',
            f'/admin/core/backupfile/restore-backup/{obj.pk}/',
            f'/admin/core/backupfile/delete-backup/{obj.pk}/',
        )
    action_buttons.short_description = 'Actions'

    def file_size_display(self, obj):
        if obj.file_size:
            return f"{obj.file_size:,} bytes"
        return "Unknown"
    file_size_display.short_description = 'File Size'

    def exists(self, obj):
        return obj.exists
    exists.boolean = True
    exists.short_description = 'File Exists'

    def has_add_permission(self, request):
        return False  # Prevent manual addition  

    def get_db_config(self):
        db_settings = settings.DATABASES['default']
        return {
            'name': db_settings['NAME'],
            'user': db_settings['USER'],
            'password': db_settings['PASSWORD'],
            'host': db_settings['HOST'],
            'port': db_settings['PORT']
        }

    def get_backup_dir(self):
        backup_dir = getattr(settings, 'PG_COPY_BACKUP_PATH', 'lod_db_backup/')
        if not os.path.isabs(backup_dir):
            backup_dir = os.path.join(settings.BASE_DIR, backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def refresh_backup_list(self):
        backup_dir = self.get_backup_dir()

        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]

            for filename in backup_files:
                file_path = os.path.join(backup_dir, filename)
                file_size = os.path.getsize(file_path)

                BackupFile.objects.get_or_create(
                    filename=filename,
                    defaults={'file_size': file_size}
                )

            existing_files = set(backup_files)
            BackupFile.objects.exclude(filename__in=existing_files).delete()

    def create_backup_view(self, request):
        try:
            db_config = self.get_db_config()
            backup_dir = self.get_backup_dir()

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

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                file_size = os.path.getsize(backup_path)
                BackupFile.objects.create(filename=filename, file_size=file_size)
                messages.success(request, f'Backup created successfully: {filename}')
            else:
                messages.error(request, f'Backup failed: {result.stderr}')

        except Exception as e:
            messages.error(request, f'Backup failed: {str(e)}')

        return redirect('admin:core_backupfile_changelist')

    def restore_backup_view(self, request, backup_id):
        try:
            backup_file = BackupFile.objects.get(pk=backup_id)

            if not backup_file.exists:
                messages.error(request, 'Backup file not found on filesystem')
                return redirect('admin:core_backupfile_changelist')

            db_config = self.get_db_config()

            cmd = [
                'psql',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['name'],
                '-f', backup_file.file_path,
                '--quiet'
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                messages.success(request, f'Database restored successfully from {backup_file.filename}')
            else:
                messages.error(request, f'Restore failed: {result.stderr}')

        except BackupFile.DoesNotExist:
            messages.error(request, 'Backup file not found')
        except Exception as e:
            messages.error(request, f'Restore failed: {str(e)}')

        return redirect('admin:core_backupfile_changelist')

    def delete_backup_view(self, request, backup_id):
        try:
            backup_file = BackupFile.objects.get(pk=backup_id)
            filename = backup_file.filename

            backup_file.delete_file()
            backup_file.delete()

            messages.success(request, f'Backup {filename} deleted successfully')

        except BackupFile.DoesNotExist:
            messages.error(request, 'Backup file not found')
        except Exception as e:
            messages.error(request, f'Delete failed: {str(e)}')

        return redirect('admin:core_backupfile_changelist')

    def refresh_backups_view(self, request):
        self.refresh_backup_list()
        messages.success(request, 'Backup list refreshed')
        return redirect('admin:core_backupfile_changelist')


# Keep your existing ContactMessage admin unchanged
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
