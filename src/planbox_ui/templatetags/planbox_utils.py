import json
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.filter
def as_json(data):
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    # If we come across </script>, we must assume that it's a part of a string
    # and neutralize it.
    json_data = json_data.replace('</script>', '<" + "/script>')
    return mark_safe(json_data)
