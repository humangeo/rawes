import unittest

from mock import patch, MagicMock
from rawes.elastic import Elastic
from requests.models import Response


class TestConnectionPooling(unittest.TestCase):
    """Connection pooling was added on top of Rawes, it wasn't designed from
    the beggingin. We need some tests to ensure our expectations of the
    connection pooling are met.
    """

    def testBasicRoundRobin(self):
        """ Set up a client with three different hosts to connect to, make
        multiple calls and check that each call goes on a different host in a
        Round Robin fashion
        """
        hosts = ['http://someserver1:9200', 'http://someserver2:9200',
                 'http://someserver3:9200']
        es = Elastic(hosts)
        with patch('rawes.http_connection.requests.Session.request',
                MagicMock(return_value=None)) as request:
            request.return_value = Response()
            called = []
            for _ in xrange(len(hosts)):
                es.get()
                # Save a list of called hosts (and remove trailing /)
                called.append(request.call_args[0][1][:-1])
            # Check against original hosts list
            self.assertSetEqual(set(hosts), set(called),
                            'All hosts in coonnection pool should be used')
            called_again = []
            for _ in xrange(len(hosts)):
                es.get()
                # Call the same hosts again (don't forget about the trailing /)
                called_again.append(request.call_args[0][1][:-1])
            # Check they were called in the same order as before
            self.assertListEqual(called, called_again,
                                    'Round robin order wasn\'t preserved')
