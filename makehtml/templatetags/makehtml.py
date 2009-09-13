from django import template
from django.template import Context
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string, select_template
import django.dispatch
from django.db.models import Model

register = template.Library()
template_chosen = django.dispatch.Signal(providing_args=["obj", "template"])
context_populated = django.dispatch.Signal(providing_args=["obj", "context"])

import logging
logging.getLogger().setLevel(logging.DEBUG)

def _iterate_names(obj, names):
    """
    Inspect an object for a value that might have multiple names.
    """
    default_value = None
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default_value

def _select_helper_template(obj, template_kind):
    """
    Generate a list of possible template names, and then select the right one.
    
    The names it tries are:
    
    - [obj.template].html 
    - [app_label]_[model]_[id]_[template_kind].html
    - [app_label]_[model]_[template_kind].html
    - [model]_[id]_[template_kind].html
    - [model]_[template_kind].html
    - [class]_[id]_[template_kind].html
    - [class]_[template_kind].html    
    - [template_kind].html
    """
    # 1.0 Determine the template
    template_names = []

    # Could be hard coded
    if hasattr(obj, 'template_name'):
        template_names.append(getattr(obj, 'template_name'))

    # Could be a django model
    if isinstance(obj, Model):
        content_type = ContentType.objects.get_for_model(obj)
        # [app_label]_[model]_[id]_[template_kind].html
        template_names.append("%s_%s_%s_%s.html" % (content_type.app_label, content_type.model, obj.id, template_kind))
        # [app_label]_[model]_[template_kind].html
        template_names.append("%s_%s_%s.html" % (content_type.app_label, content_type.model, template_kind))
        # [model]_[id]_[template_kind].html
        template_names.append("%s_%s_%s.html" % (content_type.model, obj.id, template_kind))
        # [model]_[template_kind].html
        template_names.append("%s_%s.html" % (content_type.model, template_kind))
    else:            
        # By class and ID    
        class_name = obj.__class__.__name__.lower()
        if hasattr(obj, 'id'):
            # [class]_[id]_[template_kind].html
            template_names.append('%s_%s_%s.html' % (class_name, getattr(obj, 'id'), template_kind))
        # [class]_[template_kind].html    
        template_names.append("%s_%s.html" % (class_name, template_kind))

    # Fallback template - [template_kind].html
    template_names.append('makehtml/%s.html' % template_kind)
    template = select_template(template_names)
    template_chosen.send(sender=None, obj=obj, template_chosen=template)
    return template

def _populate_context(obj, context):
    """
    Populate the context with common elements
    """
    context['title'] = _iterate_names(obj, ['title', 'name', 'headline'])
    context['body'] = _iterate_names(obj, ['body', 'content', 'text', 'note', 'description', 'long_description', 'message', 'question', 'choice'])
    context['summary'] = _iterate_names(obj, ['summary', 'excerpt', 'short_description'])    
    context['first_name'] = _iterate_names(obj, ['first_name', 'firstname'])
    context['last_name'] = _iterate_names(obj, ['last_name', 'lastname'])
    context['sub_title'] = _iterate_names(obj, ['sub_title', 'subtitle'])
    context['author'] = _iterate_names(obj, ['author', 'creator'])
    context['email'] = _iterate_names(obj, ['email'])
    context['pub_date'] = _iterate_names(obj, ['pub_date', 'timestamp', 'publish_on', 'published_on', 'creation_date', 'date_added'])
    context['thumbnail'] = _iterate_names(obj, ['thumbnail', 'thumbnail_url'])
    context['mp3_url'] = _iterate_names(obj, ['mp3_url', 'podcast_url'])    
    context['categories'] = _iterate_names(obj, ['categories', 'category', 'category_set'])
    context['is_public'] = _iterate_names(obj, ['is_public', 'published'])
    context['obj'] = obj
    # TODOs:
    # URLs
    # Event: start/stop
    return context

@register.filter(name='html')
def html(value, htmltype='summary'):
    """Introspect an object to create HTML."""
    template = _select_helper_template(value, htmltype)
    context = _populate_context(value, Context())

    context_populated.send(sender=None, obj=value, context=context)
    logging.debug("Made HTML '%s'" % htmltype)
    
    return template.render(context)
    
