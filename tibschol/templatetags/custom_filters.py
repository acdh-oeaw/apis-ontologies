import re

from django import template

register = template.Library()


@register.filter
def linebreak_split(value):
    return value.splitlines()


@register.filter
def parse_comment(value):
    pattern = r"<<(.*?) \[(.*?)\]>>"

    # subbed = re.sub(pattern, r'<a href="\2">\1</a>', value)
    # pattern = r"<<(.*?) \[([^\]]+)/([^]]+)]>>"

    subbed = re.sub(pattern, r'<a href="/bibsonomy/references/\2">\1</a>', value)

    return subbed
