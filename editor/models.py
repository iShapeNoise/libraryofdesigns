from django.db import models
from django.contrib.auth.models import User


class CADProject(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    openscad_code = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RenderJob(models.Model):
    project = models.ForeignKey(CADProject, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ])
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
