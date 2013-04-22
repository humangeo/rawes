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
    import json  # noqa

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from rawes.thrift_elasticsearch import Rest
from rawes.thrift_elasticsearch.ttypes import Method, RestRequest

from elastic_exception import ElasticException


class ThriftConnection(object):
    """Connects to elasticsearch over thrift protocol"""
    def __init__(self, host, port, timeout=None, except_on_error=False, **kwargs):
        self.protocol = 'thrift'
        self.host = host
        self.port = port
        self.except_on_error = except_on_error
        tsocket = TSocket.TSocket(self.host, self.port)
        if timeout is not None:
            tsocket.setTimeout(timeout * 1000)  # thrift expects ms
        transport = TTransport.TBufferedTransport(tsocket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Rest.Client(protocol)
        transport.open()
        self.kwargs = kwargs

    method_mappings = {
        'get': Method.GET,
        'post': Method.POST,
        'put': Method.PUT,
        'delete': Method.DELETE,
        'head': Method.HEAD
    }

    def request(self, method, path, **kwargs):
        newkwargs = self.kwargs.copy()
        newkwargs.update(kwargs)
        thriftargs = {}

        if 'data' in newkwargs:
            thriftargs['body'] = newkwargs['data']

        if 'params' in newkwargs:
            thriftargs['parameters'] = self._dict_to_map_str_str(newkwargs['params'])

        if 'headers' in newkwargs:
            thriftargs['headers'] = self._dict_to_map_str_str(newkwargs['headers'])

        mapped_method = ThriftConnection.method_mappings[method]
        request = RestRequest(method=mapped_method, uri=path, **thriftargs)
        response = self.client.execute(request)

        return self._decode(response)

    def _decode(self, response):
        if not response.body:
            decoded = response.status < 300
        else:
            decoded = json.loads(response.body)
        if self.except_on_error and response.status >= 400:
            raise ElasticException(message="ElasticSearch Error: %r" % response.body,
                                   result=decoded, status_code=response.status)
        return decoded

    def _dict_to_map_str_str(self, d):
        """
        Thrift requires the params and headers dict values to only contain str values.
        """
        return dict(map(
            lambda (k, v): (k, str(v).lower() if isinstance(v, bool) else str(v)),
            d.iteritems()
        ))
