#
#   Copyright 2012 The HumanGeo Group, LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import datetime
import pytz
import json
from rawes.utils import isstr

def encode_custom(obj):
    """
    ISO encode datetimes with less precision
    """
    if isinstance(obj, datetime.datetime):
        return obj.astimezone(pytz.utc).strftime('%Y-%m-%d')
    raise TypeError(repr(obj) + " is not JSON serializable")

class DateAwareJsonDecoder(json.JSONDecoder):
    """
    Automatically decode Y-m-d strings to python datetime objects in UTC timezone
    """
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)
    
    def dict_to_object(self, d):
        for k,v in d.items():
            if isstr(v):
                try:
                    d[k] = pytz.utc.localize(datetime.datetime.strptime( v, "%Y-%m-%d"))
                except Exception as e:
                    pass
        return d
