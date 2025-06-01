from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Thing(models.Model):
    save_path = datetime.now()
    save_path = save_path.strftime("%Y%m%d%H%M%S")+'/'
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='things',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # use blank=False if you want * the description
    description = models.TextField(blank=True, null=True)
    costs = models.FloatField()

    image = models.ImageField(upload_to=save_path+'images/',
                              blank=True, 
                              null=False)
    name = models.CharField(max_length=255)
    is_modified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='things',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
