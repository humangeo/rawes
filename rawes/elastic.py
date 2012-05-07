from thrift_connection import ThriftConnection
from http_connection import HttpConnection
from index_set import IndexSet

class Elastic(object):
    """Connect to an elasticsearch instance"""
    def __init__(self, url='localhost:9200', timeout=30, connection_type=None):
        super(Elastic, self).__init__()
        url_parts = url.split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) == 2 else 9200
        self.timeout = timeout*1000
        
        if (connection_type == None):
            self.connection_type = 'http' if self.port == 9200 else 'thrift'
        else:
            self.connection_type = connection_type
        
        if (self.connection_type == 'http'):
            self.connection = HttpConnection(self.host, self.port)
        else:
            self.connection = ThriftConnection(self.host, self.port)
    
    def put(self, path, **kwargs):
        return self.connection.put(path, **kwargs)

    def get(self, path, **kwargs):
        return self.connection.get(path, **kwargs)
            
    def post(self, path, **kwargs):
        return self.connection.post(path, **kwargs)
    
    def delete(self, path, **kwargs):
        return self.connection.delete(path, **kwargs)
    
    def __getitem__(self, indices):
        return IndexSet(indices, self)
