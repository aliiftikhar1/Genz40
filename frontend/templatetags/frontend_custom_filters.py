# frontend/templatetags/frontend_custom_filters.py

from django import template
import re

register = template.Library()


@register.filter
def truncate_chars(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='without_label')
def without_label(field):
    return field.as_widget(attrs={'class': 'form-control', 'placeholder': field.label})


@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def title_case(value):
    """
    Converts comma-separated values into title case
    E.g., 'engineMounts,gurneyBubble' to 'EngineMounts, GurneyBubble'
    """
    if not value:
        return ''
    
    # Split the string by commas
    parts = value.split(',')
    
    # Title case each part (convert first letter of each word to uppercase)
    # This handles camelCase by finding capital letters and adding spaces before them
    formatted_parts = []
    for part in parts:
        # Convert first letter to uppercase
        if part:
            # Handle camelCase by keeping existing capital letters
            formatted = part[0].upper() + part[1:]
            formatted_parts.append(formatted)
    
    # Join parts with comma and space
    return ', '.join(formatted_parts)


@register.filter
def truncate_lines(value, max_lines):
    """
    Truncates text to a specified number of lines.
    If text has more lines than max_lines, adds '...' at the end.
    Preserves existing line breaks in the output.
    """
    if not value:
        return value
    
    lines = value.splitlines()
    
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + '...'
    return value