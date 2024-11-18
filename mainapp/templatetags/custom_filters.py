from django import template
import re

register = template.Library()

@register.filter
def format_text(value):
    # Split by new lines to create paragraphs
    paragraphs = value.split('\n')
    formatted = []
    
    for para in paragraphs:
        if para.strip().startswith('-'):
            # If a paragraph starts with "-", consider it a list item
            items = para.split('-')[1:]  # Skip the first empty split
            formatted.append('<ul>' + ''.join(f'<li>{item.strip()}</li>' for item in items if item.strip()) + '</ul>')
        else:
            # Otherwise, create a paragraph
            formatted.append(f'<p>{para.strip()}</p>')
    
    return ''.join(formatted)


