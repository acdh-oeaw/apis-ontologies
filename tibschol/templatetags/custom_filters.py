from django import template

register = template.Library()


@register.filter
def linebreak_split(value):
    return value.splitlines()
