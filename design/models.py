import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
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

    def get_total_design_count(self):
        """
        Return total count of designs in this category and all its descendants
        """
        # Get all descendant categories including self
        descendant_categories = self.get_descendants(include_self=True)

        # Count designs in all these categories
        from .models import Design
        return Design.objects.filter(category__in=descendant_categories).count()


# Create custom storage for LOD content  
lod_storage = FileSystemStorage(
    location=os.path.join(settings.LOD_CONTENT_ROOT, 'tmp'),
    base_url='/lod_content/tmp/'
)

# Ensure tmp directories exist - ADD THIS SECTION HERE
tmp_images_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'tmp', 'images')
tmp_techdraws_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'tmp', 'techdraws')

os.makedirs(tmp_images_dir, exist_ok=True)
os.makedirs(tmp_techdraws_dir, exist_ok=True)


def design_image_path(instance, filename):
    """
    Generate upload path for design images in LOD content directory
    """
    return os.path.join('images', filename)


def design_techdraw_path(instance, filename):
    """
    Generate upload path for design images in LOD content directory
    """
    return os.path.join('techdraws', filename)


lod_storage = FileSystemStorage(
    location=os.path.join(settings.LOD_CONTENT_ROOT, 'tmp'),
    base_url='/lod_content/tmp/'
)


class Design(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='designs',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # use blank=False if you want * the description
    description = models.TextField()
    costs = models.FloatField()
    production_notes = models.TextField(blank=True, null=True)
    path_to_save = unique_file_path()
    image = models.ImageField(
        upload_to=design_image_path,
        storage=lod_storage)
    image_list = models.TextField(blank=True, null=True)
    techdraw = models.FileField(
        upload_to=design_techdraw_path,
        storage=lod_storage,
        blank=True,
        null=True)
    techdraw_list = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255)
    added_by = models.ForeignKey(User, related_name='added_designs',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    is_modified = models.BooleanField(default=False)
    modified_from = models.URLField(null=True,
                                    blank=True,
                                    help_text="URL of LoD Design to determine predecessor")
    created_by = models.ForeignKey(User, related_name='created_designs',
                                   on_delete=models.CASCADE,
                                   help_text="Add name of creator/modifier of new design")
    custom_creator_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    utilities = models.TextField(blank=True, null=True)
    module = models.TextField()
    example = models.TextField()

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            # Manually construct URL for LoD content
            return f"{settings.LOD_CONTENT_URL}{self.image.name}"
        return None


class BillOfMaterials(models.Model):
    bom_design = models.ForeignKey(Design,
                                   related_name='bom_items',
                                   on_delete=models.CASCADE)
    bom_position = models.IntegerField()
    bom_count = models.IntegerField(default=1)
    bom_name = models.CharField(max_length=255)
    bom_standard = models.CharField(max_length=255, blank=True, null=True)
    bom_material = models.CharField(max_length=255, blank=True, null=True)
    bom_notes = models.TextField(blank=True, null=True)
    bom_link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['bom_position']

    def __str__(self):
        return f"{self.design.name} - {self.name}"
