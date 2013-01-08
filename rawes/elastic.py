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

from thrift_connection import ThriftConnection
from http_connection import HttpConnection
from rawes.encoders import encode_date_optional_time

class Elastic(object):
    """Connect to an elasticsearch instance"""
    def __init__(self, url='localhost:9200', path='', timeout=30, connection_type=None, connection=None, except_on_error=False):
        super(Elastic, self).__init__()
        url_parts = url.split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) == 2 else 9200
        self.url = '%s:%s' % (self.host, self.port)
        self.timeout = timeout # seconds
        self.path = path

        if connection_type is None:
            if self.port >= 9500 and self.port <= 9600:
                self.connection_type = 'thrift'
            else:
                self.connection_type = 'http'
        else:
            self.connection_type = connection_type

        if connection is None:
            if self.connection_type == 'http':
                self.connection = HttpConnection(self.host, self.port, timeout=self.timeout, except_on_error=except_on_error)
            else:
                self.connection = ThriftConnection(self.host, self.port, timeout=self.timeout, except_on_error=except_on_error)
        else:
            self.connection = connection

    def put(self, path='', **kwargs):
        return self.request('put', path, **kwargs)

    def get(self, path='', **kwargs):
        return self.request('get', path, **kwargs)

    def post(self, path='', **kwargs):
        return self.request('post', path, **kwargs)

    def delete(self, path='', **kwargs):
        return self.request('delete', path, **kwargs)

    def head(self, path='', **kwargs):
        return self.request('head', path, **kwargs)

    def request(self, method, path, **kwargs):
        new_path = self._build_path(self.path, path)

        # Look for a custom json encoder
        if 'json_encoder' in kwargs:
            json_encoder = kwargs['json_encoder']
            del kwargs['json_encoder']
        else:
            json_encoder = encode_date_optional_time

        # Encode data dict to json if necessary
        if 'data' in kwargs and type(kwargs['data']) == dict:
            kwargs['data'] = json.dumps(kwargs['data'], default=json_encoder)

        return self.connection.request(method, new_path, **kwargs)

    def __getattr__(self, path_item):
        return self.__getitem__(path_item)

    def __getitem__(self, path_item):
        new_path = self._build_path(self.path, path_item)
        return Elastic(
            url=self.url,
            timeout=self.timeout,
            connection_type=self.connection_type,
            path=new_path,
            connection=self.connection
        )

    def _build_path(self, base_path, path_item):
        return '%s/%s' % (base_path, path_item) if base_path != '' else path_item
