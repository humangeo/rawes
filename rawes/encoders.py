import datetime
from dateutil import tz

def encode_datetime(obj):
    """
    ISO encode datetimes
    """
    if isinstance(obj, datetime.datetime):
        return obj.astimezone(tz.tzutc()).strftime('%Y-%m-%dT%H:%M:%SZ')
    raise TypeError(repr(obj) + " is not JSON serializable")