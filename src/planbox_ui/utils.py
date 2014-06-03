import sys
from django.utils.html_parser import HTMLParser, HTMLParseError


class MLStripper(HTMLParser):
    def __init__(self):
        # The strict parameter was added in Python 3.2 with a default of True.
        # The default changed to False in Python 3.3 and was deprecated.
        if sys.version_info[:2] == (3, 2):
            HTMLParser.__init__(self, strict=False)
        else:
            HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)

    def handle_charref(self, name):
        self.fed.append('&#%s;' % name)

    def get_data(self, joinstr=''):
        return joinstr.join(self.fed)


def _strip_once(value, joinstr):
    """
    Internal tag stripping utility used by strip_tags.
    """
    s = MLStripper()
    try:
        s.feed(value)
    except HTMLParseError:
        return value
    try:
        s.close()
    except (HTMLParseError, UnboundLocalError):
        # UnboundLocalError because of http://bugs.python.org/issue17802
        # on Python 3.2, triggered by strict=False mode of HTMLParser
        return s.get_data(joinstr) + s.rawdata
    else:
        return s.get_data(joinstr)


def strip_tags(value, joinstr=''):
    """Returns the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    while '<' in value and '>' in value:
        new_value = _strip_once(value, joinstr)
        if new_value == value:
            # _strip_once was not able to detect more tags
            break
        value = new_value
    return value
