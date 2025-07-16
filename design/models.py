import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid
# from easy_thumbnails.fields import ThumbnailerImageField
from mptt.models import MPTTModel, TreeForeignKey


def unique_file_path():
    path_name = "%s" % (uuid.uuid4())
    return str(path_name)


class Category(MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_full_path(self):
        """
        Return full category path like 'Electronics > Computers > Laptops'
        """
        return ' > '.join([ancestor.name for ancestor in self.get_ancestors(include_self=True)])


def design_image_path(instance, filename):
    """
    Generate upload path for design images in LOD content directory
    """
    return os.path.join('images', filename)


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
    image = models.ImageField(upload_to=design_image_path,
                              blank=False,
                              null=True)
    name = models.CharField(max_length=255)
    is_modified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='designs',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            # Manually construct URL for LoD content
            return f"{settings.LOD_CONTENT_URL}{self.image.name}"
        return None
