from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone


class ForumCategory(MPTTModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    position = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['position', 'name']

    class Meta:
        verbose_name_plural = 'Forum Categories'
        ordering = ['position', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forum:category', kwargs={'pk': self.pk})


class Topic(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sticky = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-sticky', '-updated']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:topic', kwargs={'pk': self.pk})

    @property
    def post_count(self):
        return self.posts.count()

    @property
    def last_post(self):
        return self.posts.order_by('-created').first()


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Post by {self.created_by.username} in {self.topic.title}'

    def get_absolute_url(self):
        return reverse('forum:topic', kwargs={'pk': self.topic.pk}) + f'#post-{self.pk}'
