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
import urlparse
try:
    import simplejson as json
except ImportError:
    import json  # noqa

from http_connection import HttpConnection
from rawes.encoders import encode_date_optional_time


class Elastic(object):
    """Connect to an elasticsearch instance"""
    def __init__(self, url='localhost:9200', path='', timeout=30, connection=None, except_on_error=False, **kwargs):
        super(Elastic, self).__init__()

        self.url = self._decode_url(url,path)
        self.timeout = timeout  # seconds

        if connection is None:
            if self.url.scheme == 'http' or self.url.scheme == 'https':
                connection = HttpConnection(self.url.geturl(), timeout=self.timeout, except_on_error=except_on_error, **kwargs)
            else:
                try:
                    from thrift_connection import ThriftConnection
                except ImportError:
                    raise ImportError("The 'thrift' python package does not seem to be installed.")
                connection = ThriftConnection(self.url.hostname, self.url.port, timeout=self.timeout, except_on_error=except_on_error, **kwargs)

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
        return '%s/%s' % (base_path, path_item) if base_path != '' else path_item

    def _decode_url(self, url, path):
        # Make sure urlsplit() doesn't choke on scheme-less URLs, like 'localhost:9200'
        if '//' not in url:
            url = '//' + url

        url = urlparse.urlsplit(url)
        if not url.netloc:
            raise ValueError('Could not parse the given URL.')

        # If the scheme isn't explicitly provided by now, try to deduce it
        # from the port number
        scheme = url.scheme
        if not scheme:
            if 9500 <= url.port <= 9600:
                scheme = 'thrift'
            else:
                scheme = 'http'

        # Use path if provided
        if not path:
            path = url.path

        # Set default ports
        netloc = url.netloc
        if not url.port:
            if url.scheme == 'http':
                netloc = "%s:%s" % (netloc,9200)
            elif url.scheme == 'https':
                netloc = "%s:%s" % (netloc,443)
            elif url.scheme == 'thrift':
                netloc = "%s:%s" % (netloc,9500)

        # Return new url. 
        return urlparse.SplitResult(scheme=scheme, netloc=netloc, path=path, query='', fragment='')

