import json

try:
    from thrift import Thrift
    from thrift.transport import TSocket
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol

    from thrift_elasticsearch import Rest
    from thrift_elasticsearch.ttypes import Method, RestRequest
    thrift_installed=True
except ImportError:
    thrift_installed=False

class ThriftConnection(object):
    """docstring for ThriftConnection"""
    def __init__(self, host, port):
        if not thrift_installed:
            raise(Exception("The 'thrift' Python module does not appear to be installed.  Please install it before creating a ThriftConnection"))
        self.protocol = 'thrift'
        self.host = host
        self.port = port
        self.url = '%s://%s:%s' % (self.protocol,self.host,self.port)
        tsocket = TSocket.TSocket(self.host, self.port)
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
        if kwargs.has_key('data'):
            if type(kwargs['data']) == dict:
                kwargs['data'] = json.dumps(kwargs['data'])
            thriftargs['body'] = kwargs['data']

        if kwargs.has_key('params'):
            thriftargs['parameters'] = kwargs['params']

        if kwargs.has_key('headers'):
            thriftargs['headers'] = kwargs['headers']

        request = RestRequest(method=method,uri=path,**thriftargs)
        response = self.client.execute(request)

        return ThriftConnection.decode(response)
    
    @classmethod
    def decode(self, response):
        if (response.body == ''):
            return response.status < 300
        return json.loads(response.body)
            