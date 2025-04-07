from django import template
import re
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

@register.filter
def convert_hashtags(value):
    hashtag_pattern = r'#(\w+)'
    result = re.sub(hashtag_pattern,
                    lambda match: f'<a href="{reverse("tags", args=[match.group(1)])}">#{match.group(1)}</a>',
                    value)
    return mark_safe(result)
