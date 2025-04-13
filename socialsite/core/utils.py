import re
from django.urls import reverse
from django.utils.html import escape
def parse_caption(text):
    # Escape HTML first
    text = escape(text)