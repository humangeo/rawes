import urllib

def build_query_string(params):
    """Returns a query string with leading ?"""
    return '?%s' % urllib.urlencode(params) if len(params) else ''