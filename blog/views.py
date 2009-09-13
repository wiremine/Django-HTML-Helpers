from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404
from django.template import RequestContext

from helpers.blog.models import Post

def index(request):
    posts = Post.objects.all()

    return render_to_response('blog/index.html', {
        'posts': posts
    }, context_instance=RequestContext(request))