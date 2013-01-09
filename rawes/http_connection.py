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

try:
    import simplejson as json
except ImportError:
    import json

import requests
from elastic_exception import ElasticException

class HttpConnection(object):
    """docstring for HttpConnection"""
    def __init__(self, host, port, timeout=None, except_on_error=False):
        super(HttpConnection, self).__init__()
        self.protocol = 'http'
        self.host = host
        self.port = port
        self.timeout = timeout
        #self.session = requests.session(timeout=timeout) # requests expects seconds
        self.session = requests.session() # requests expects seconds
        self.url = '%s://%s:%s' % (self.protocol, self.host, self.port)
        self.except_on_error = except_on_error

    def request(self, method, path, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.session.request(method, '%s/%s' % (self.url, path), **kwargs)
        return self._decode(response)

    def _decode(self, response):
        if (response.text == ''):
            decoded = response.status_code < 300
        else:
            decoded = json.loads(response.text)
        if (self.except_on_error and response.status_code >=400):
            raise(ElasticException(message="ElasticSearch Error: %r" % response.text, result=decoded, status_code=response.status_code))
        return decoded
