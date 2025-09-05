from django.db import models
import os
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=100)  # 'lod', 'cad', 'cam'  
    title = models.CharField(max_length=200)
    folder_path = models.CharField(max_length=200)

    def get_about_content(self):
        about_path = os.path.join(settings.LOD_CONTENT_ROOT, 'know-how', self.folder_path, 'about.md')
        if os.path.exists(about_path):
            with open(about_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_index_content(self):
        index_path = os.path.join(settings.LOD_CONTENT_ROOT, 'know-how', self.folder_path, 'index.md')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
