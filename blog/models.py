from django.db import models
from django.utils.translation import ugettext_lazy as _

class Post(models.Model):
    """A blog post"""
    title = models.CharField(blank=True, max_length=100)
    body = models.TextField(blank=True)
    timestamp = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['timestamp']


