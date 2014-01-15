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

import requests
from .elastic_exception import ElasticException


class HttpConnection(object):
    """Connects to elasticsearch over HTTP"""
    def __init__(self, url, timeout=None, **kwargs):
        super(HttpConnection, self).__init__()
        self.protocol = 'http'
        self.url = url
        self.timeout = timeout
        self.kwargs = kwargs
        self.session = requests.session()

    def request(self, method, path, **kwargs):
        args = self.kwargs.copy()
        args.update(kwargs)

        if "json_decoder" in args:
            json_decoder = args["json_decoder"]
            del args["json_decoder"]
        else:
            json_decoder = json.loads

        if 'timeout' not in args:
            args['timeout'] = self.timeout
        response = self.session.request(method,
                                        "/".join((self.url, path)), **args)
        return self._decode(response, json_decoder)

    def _decode(self, response, json_decoder):
        if not response.text:
            decoded = response.status_code < 300
        else:
            try:
                decoded = json_decoder(response.text)
            except ValueError:
                decoded = False

        if response.status_code >= 400:
            raise ElasticException(
                    message="ElasticSearch Error: {0}".format(response.text),
                    result=decoded, status_code=response.status_code)
        return decoded
