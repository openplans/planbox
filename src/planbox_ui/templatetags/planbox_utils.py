from __future__ import unicode_literals

import json
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from planbox_ui.utils import strip_tags

register = Library()

@register.filter
def as_json(data):
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    # If we come across </script>, we must assume that it's a part of a string
    # and neutralize it.
    json_data = json_data.replace('</script>', '<" + "/script>')
    return mark_safe(json_data)


@register.filter(is_safe=True)
@stringfilter
def striptags(value, joinstr=''):
    """Strips all [X]HTML tags."""
    new_value = strip_tags(value, joinstr)
    return re.sub('\s+', ' ', new_value)

@register.filter
def force_list(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return value
    else:
        return [value]
