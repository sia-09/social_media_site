from django import template
import re
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

@register.filter
def mentionify(text):
    def repl(match):
        username = match.group(1)
        url = reverse('view_profile', args=[username])
        return f'<a href="{url}" class="text-blue-400 hover:underline">@{username}</a>'

    return mark_safe(re.sub(r'@(\w+)', repl, text))
