import re

EXTRA_SPACE_REGEX = re.compile(r'\s+')
def remove_extra_spaces(string):
    return re.sub(EXTRA_SPACE_REGEX, " ", string)