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

from rawes.encoders import encode_datetime

try:
    from thrift import Thrift
    from thrift.transport import TSocket
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol

    from rawes.thrift_elasticsearch import Rest
    from rawes.thrift_elasticsearch.ttypes import Method, RestRequest
    thrift_installed = True
except ImportError:
    thrift_installed = False


class ThriftConnection(object):
    """Connects to elasticsearch over thrift protocol"""
    def __init__(self, host, port, timeout=None):
        if not thrift_installed:
            raise(Exception("The 'thrift' Python module does not appear to be installed.  Please install it before creating a ThriftConnection"))
        self.protocol = 'thrift'
        self.host = host
        self.port = port
        self.url = '%s://%s:%s' % (self.protocol, self.host, self.port)
        tsocket = TSocket.TSocket(self.host, self.port)
        if timeout is not None:
            tsocket.setTimeout(timeout * 1000)
        transport = TTransport.TBufferedTransport(tsocket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Rest.Client(protocol)
        transport.open()

    def get(self, path, **kwargs):
        return self.request(Method.GET, path, **kwargs)

    def post(self, path, **kwargs):
        return self.request(Method.POST, path, **kwargs)

    def put(self, path, **kwargs):
        return self.request(Method.PUT, path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request(Method.DELETE, path, **kwargs)

    def head(self, path, **kwargs):
        return self.request(Method.HEAD, path, **kwargs)

    def request(self, method, path, **kwargs):
        thriftargs = {}

        if 'data' in kwargs:
            body = kwargs['data']
            if type(kwargs['data']) == dict:
                body = json.dumps(kwargs['data'], default=encode_datetime)
            thriftargs['body'] = body

        if 'params' in kwargs:
            thriftargs['parameters'] = self._dict_to_map_str_str(kwargs['params'])

        if 'headers' in kwargs:
            thriftargs['headers'] = self._dict_to_map_str_str(kwargs['headers'])

        request = RestRequest(method=method, uri=path, **thriftargs)
        response = self.client.execute(request)

        return self._decode(response)

    def _decode(self, response):
        if (response.body == ''):
            return response.status < 300
        return json.loads(response.body)

    def _dict_to_map_str_str(self, d):
        """
        Thrift requires the params and headers dict values to only contain str values.
        """
        return dict(map(
            lambda (k, v): (k, str(v).lower() if isinstance(v, bool) else str(v)),
            d.iteritems()
        ))
