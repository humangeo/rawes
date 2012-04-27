class ThriftConnection(object):
    """docstring for ThriftConnection"""
    def __init__(self, host, port):
        super(ThriftConnection, self).__init__()
        self.protocol = 'http'
        self.host = host
        self.port = port
        self.url = '%s://%s:%s' % (self.protocol,self.host,self.port)
        