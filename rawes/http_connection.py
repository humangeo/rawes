#
#   Copyright [2012] [Dan Noble]
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

import requests
import json


class HttpConnection(object):
    """docstring for HttpConnection"""
    def __init__(self, host, port, timeout=None):
        super(HttpConnection, self).__init__()
        self.protocol = 'http'
        self.host = host
        self.port = port
        self.session = requests.session(timeout=timeout)
        self.url = '%s://%s:%s' % (self.protocol, self.host, self.port)

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('post', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request('put', path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request('delete', path, **kwargs)

    def head(self, path, **kwargs):
        return self.request('head', path, **kwargs)

    def request(self, method, path, **kwargs):
        if 'data' in kwargs and type(kwargs['data']) == dict:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = self.session.request(method, '%s/%s' % (self.url, path), **kwargs)
        return self._decode(response)

    def _decode(self, response):
        if (response.text == ''):
            return response.status_code < 300
        return json.loads(response.text)
