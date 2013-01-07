class ElasticException(Exception):
    def __init__(self, message, result, status_code):
        Exception.__init__(self, message)
        self.result = result
        self.status_code = status_code
