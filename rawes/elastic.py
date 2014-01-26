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

import re
import sys

from .connection_pool import ConnectionPool
from .encoders import encode_date_optional_time
from .http_connection import HttpConnection
try:
    import simplejson as json
except ImportError:
    import json  # noqa

if sys.version_info[0] > 2:
    import urllib.parse as urlparse
else:
    import urlparse


class Elastic(object):
    """Connect to an elasticsearch instance"""

    def __init__(self, url='localhost:9200', path='', timeout=30,
                 connection=None,
                 json_encoder=encode_date_optional_time,
                 connection_pool=None, **kwargs):
        """Constructs an :class:`Elastic <Elastic>`, client object.
        Returns :class:`Elastic <Elastic>` object.

        :param url: (optional) URL for the host the client will conenct to.
            A list of URL's can be provided if you want to use a connection
            pool for your requests. Each new call will use a different host
            from the conenction pool. If you don't provide any arguments to
            this constructor then the default url will be used.
        :param path: (optional) elasticserach api path you want to make the
            call to.
        :param timeout: (optional) an integer specifying the number of seconds
            to wait before timing out a call
        :param connection: (optional) if you already have a connection object
            that you want to use you can pass it in here; in this case, the
            url and timeout values will be ignored
        :param json_encoder: (optional) customize the way you encode data sent
            over to elasticsearch
        :param connection_pool: (optional) if you have a connection pool object
            that you want to reuse you can pass it in here; in this case, the
            url value will be ignored
        """

        super(Elastic, self).__init__()

        if not isinstance(url, list) and not isinstance(url, str):
            raise ValueError('Url provided is not of right type')

        # Clean up url of any path items
        if isinstance(url, str):
            decoded_url = self._decode_url(url, '')
            path = self._build_path(decoded_url.path, path)
            url = decoded_url.netloc
            if decoded_url.scheme:
                url = '{0}://{1}'.format(decoded_url.scheme, url)

        if connection_pool is None:
            if connection is None:
                urls = [url] if isinstance(url, str) else url
                # Validate all urls are of correct format host:port
                for host_url in urls:
                    if '//' not in host_url:
                        host_url = '//' + host_url
                    if urlparse.urlsplit(host_url).path not in ['', '/']:
                        raise ValueError('Url paths not allowed in hosts list')

                connection_pool = ConnectionPool([(
                                self._get_connection_from_url(host_url, timeout,
                                **kwargs), {}) for host_url in urls])

            else:
                connection_pool = ConnectionPool([(connection, None)])

        self.path = path
        self.timeout = timeout  # seconds
        self.json_encoder = json_encoder
        self.connection_pool = connection_pool

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
            json_encoder = self.json_encoder

        # Encode data dict to json if necessary
        if 'data' in kwargs and type(kwargs['data']) == dict:
            kwargs['data'] = json.dumps(kwargs['data'], default=json_encoder)

        # Always select a connection from the pool for each new request
        return self.connection_pool.get_connection().request(
                                                    method, new_path, **kwargs)

    def __getattr__(self, path_item):
        return self.__getitem__(path_item)

    def __getitem__(self, path_item):
        new_path = self._build_path(self.path, path_item)
        return Elastic(
            timeout=self.timeout,
            path=new_path,
            connection_pool=self.connection_pool
        )

    def _build_path(self, base_path, path_item):
        new_path = '/'.join((str(base_path), str(path_item))) if base_path != '' else str(path_item)
        # Clean up path of any extraneous forward slashes
        return re.sub("/{2,}", "/", new_path)

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
                netloc = "{0}:{1}".format(netloc, 9200)
            elif url.scheme == 'https':
                netloc = "{0}:{1}".format(netloc, 443)
            elif url.scheme == 'thrift':
                netloc = "{0}:{1}".format(netloc, 9500)

        # Return new url.
        return urlparse.SplitResult(scheme=scheme, netloc=netloc, path=path,
                                    query='', fragment='')

    def _get_connection_from_url(self, url, timeout, **kwargs):
        """Returns a connection object given a string url"""

        url = self._decode_url(url, "")

        if url.scheme == 'http' or url.scheme == 'https':
            return HttpConnection(url.geturl(), timeout=timeout, **kwargs)
        else:
            if sys.version_info[0] > 2:
                raise ValueError("Thrift transport is not available "
                                 "for Python 3")

            try:
                from thrift_connection import ThriftConnection
            except ImportError:
                raise ImportError("The 'thrift' python package "
                                    "does not seem to be installed.")
            return ThriftConnection(url.hostname, url.port,
                                    timeout=timeout, **kwargs)
