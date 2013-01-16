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

from urlparse import urlsplit, SplitResult
try:
    import simplejson as json
except ImportError:
    import json  # noqa

from http_connection import HttpConnection
from rawes.encoders import encode_date_optional_time


class Elastic(object):
    """Connect to an elasticsearch instance"""
    def __init__(self, url='localhost:9200', path='', timeout=30, connection=None, except_on_error=False):
        super(Elastic, self).__init__()

        if '//' not in url:
            # Make sure urlsplit() doesn't choke on scheme-less URLs, like 'localhost:9200'
            url = '//' + url

        url = urlsplit(url)
        if not url.netloc:
            raise ValueError('Could not parse the given URL.')

        # Sanitize the URL:
        # - query, fragment aren't allowed;
        # - path is used if explicitly provided;
        # - scheme is optional (will be derived from port number, if possible)
        scheme = url.scheme

        # If the scheme isn't explicitly provided by now, try to deduce it
        # from the port number
        if not scheme:
            if 9500 <= url.port <= 9600:
                scheme = 'thrift'
            else:
                scheme = 'http'

        if not path:
            path = url.path

        url = SplitResult(scheme=scheme, netloc=url.netloc, path=path, query='', fragment='')

        self.url = url
        self.timeout = timeout  # seconds

        if connection is None:
            if scheme == 'http':
                connection = HttpConnection(url, timeout=self.timeout, except_on_error=except_on_error)
            else:
                try:
                    from thrift_connection import ThriftConnection
                except ImportError:
                    raise ImportError("The 'thrift' python package does not seem to be installed.")
                connection = ThriftConnection(url, timeout=self.timeout, except_on_error=except_on_error)

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
        new_path = self._build_path(self.url.path, path)

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
        new_path = self._build_path(self.url.path, path_item)
        return Elastic(
            url=self.url.geturl(),
            timeout=self.timeout,
            path=new_path,
            connection=self.connection
        )

    def _build_path(self, base_path, path_item):
        return '/'.join([base_path, path_item]) if base_path else path_item
