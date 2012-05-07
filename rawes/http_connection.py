import requests
import json

class HttpConnection(object):
    """docstring for HttpConnection"""
    def __init__(self, host, port):
        super(HttpConnection, self).__init__()
        self.protocol = 'http'
        self.host = host
        self.port = port
        self.url = '%s://%s:%s' % (self.protocol,self.host,self.port)
    
    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)
    
    def post(self, path, **kwargs):
        return self.request('post', path, **kwargs)
    
    def put(self, path, **kwargs):
        return self.request('put', path, **kwargs)
    
    def delete(self, path, **kwargs):
        return self.request('delete', path, **kwargs)
    
    def request(self, method, path, **kwargs):
        if kwargs.has_key('data') and type(kwargs['data']) == dict:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.request(method, '%s/%s' % (self.url,path), **kwargs)
        return HttpConnection.decode(response)
    
    @classmethod
    def decode(self, response):
        """docstring for decode"""
        return json.loads(response.text)
