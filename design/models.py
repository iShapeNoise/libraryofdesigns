from django.db import models
from django.contrib.auth.models import User
import uuid
from easy_thumbnails.fields import ThumbnailerImageField


def unique_file_path():
    path_name = "%s" % (uuid.uuid4())
    return str(path_name)


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Design(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='designs',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # use blank=False if you want * the description
    description = models.TextField(blank=True, null=True)
    costs = models.FloatField()
    path_to_save = unique_file_path()
    # image = ThumbnailerImageField(upload_to=path_to_save+'/images/',
    #                              blank=False,
    #                              null=True)
    image = models.ImageField(upload_to='images/', blank=False,
                              null=True)
    name = models.CharField(max_length=255)
    is_modified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='designs',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
