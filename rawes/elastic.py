from thrift_connection import ThriftConnection
from http_connection import HttpConnection

class Elastic(object):
    """Connect to an elasticsearch instance"""
    def __init__(self, url='localhost:9200', path='', timeout=30, connection_type=None, connection=None):
        super(Elastic, self).__init__()
        url_parts = url.split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) == 2 else 9200
        self.url = '%s:%s' % (self.host, self.port)
        self.timeout = None if timeout == None else timeout*1000
        self.path=path
        
        if connection_type == None:
            if self.port >= 9500 and self.port <= 9600:
                self.connection_type = 'thrift'
            else:
                self.connection_type = 'http'
        else:
            self.connection_type = connection_type
        
        if connection == None:
            if self.connection_type == 'http':
                self.connection = HttpConnection(self.host, self.port, timeout=self.timeout)
            else:
                self.connection = ThriftConnection(self.host, self.port, timeout=self.timeout)
        else:
            self.connection = connection
    
    def put(self, path='', **kwargs):
        new_path = self._build_path(self.path, path)
        return self.connection.put(new_path, **kwargs)

    def get(self, path='', **kwargs):
        new_path = self._build_path(self.path, path)
        return self.connection.get(new_path, **kwargs)
            
    def post(self, path='', **kwargs):
        new_path = self._build_path(self.path, path)
        return self.connection.post(new_path, **kwargs)
    
    def delete(self, path='', **kwargs):
        new_path = self._build_path(self.path, path)
        return self.connection.delete(new_path, **kwargs)
    
    def head(self, path='', **kwargs):
        new_path = self._build_path(self.path, path)
        return self.connection.head(new_path, **kwargs)
    
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

    def _build_path(self, base_path,path_item):
        return '%s/%s' % (base_path,path_item) if base_path != '' else path_item
