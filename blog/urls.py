from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('helpers.blog.views',
    url(r'^$', 'index', name='blog-index'), 
)
