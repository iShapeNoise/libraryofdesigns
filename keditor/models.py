from django.db import models
from django.contrib.auth.models import User


class KidsProject(models.Model):
    name = models.CharField(max_length=100, default='My Project')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blocks_xml = models.TextField(blank=True)  # Blockly XML data  
    openscad_code = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class KidsRenderJob(models.Model):
    project = models.ForeignKey(KidsProject, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

