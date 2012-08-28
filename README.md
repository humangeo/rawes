rawes
=====

About
-----
rawes is an elasticsearch driver for Python.  It provides a small level of abstraction above the requests library - more than enough to be useful, but not enough to obscure elasticsearch's great [native api](http://www.elasticsearch.org/guide/reference/api/)

Features
--------
* elasticsearch native API support
* gzip over HTTP support
* Thrift support

Installation
------------
```bash
$ pip install rawes
```

Usage
-----
Create a connection to elasticsearch
```python
import rawes
es = rawes.Elastic('localhost:9200')
```

Search for a document
```python
es.get('tweets/tweet/_search', data={
    'query' : {
        'match_all' : {}
    }
})
```

The rawes.Elastic constructor takes the following parameters (defaults shown):
```python
rawes.Elastic(
    url='localhost:9200', # Path and port to elasticsearch service.  Ports 9500-9600 will use thrift; others http
    path='', # http url path (for example, 'tweets/tweet/_search')
    timeout=30, # Timeout in seconds
    connection_type=None, # Set to 'http' or 'thrift' to explicitly set a protocol
)
```

An instance of rawes.Elastic ('es' in this case) has methods for get, post, put, delete, and head (for each http verb).  Each method takes the following parameters (defaults shown):
```python
es.get(
    path='', # HTTP URL path
    data='', # http body.  can be either a string or a python dictionary (will automatically be converted to JSON)
    params={}, # HTTP URL params passed as a python dictionary
    headers={}, # HTTP headers as a python dictionary
    **kwargs # HTTP only: any additional parameters you wish to pass to the python 'requests' library (for example, basic auth)
)
```

Examples
--------

Create a new document in the twitter index of type tweet with id 1
```python
es.put('tweets/tweet/1', data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T08:00:30',
    'message' : 'Tweeting about elasticsearch'
})
es.put('blogs/post/2', data={
    'user' : 'dan',
    'post_date' : '2012-8-27T09:30:03',
    'title' : 'Elasticsearch',
    'body' : 'Blogging about elasticsearch'
})
```

Search for a document, specifying http params
```python
es.get('tweets/tweet/_search', data={
    'query' : {
        'match_all' : {}
    }
}, params= {
    'size': 2
})
```

Search for a document with a JSON string
```python
es.get('tweets,blogs/_search', data="""
{
    "query" : {
        "match_all" : {}
    }
}
""")
```

Update a document
```python
es.put('someindex/sometype/123', data={
    'value' : 100,
    'other' : 'stuff'
})
es.post('someindex/sometype/123/_update', data={
    'script' : 'ctx._source.value += value',
    'params' : {
        'value' : 50
    }
})
```

Delete a document
```python
es.delete('tweets/tweet/1')
```


Alternate Syntax
----------------
Instead of setting the first argument of a es.&lt;http verb&gt; call to the HTTP URL path, you can also use python attributes and items to build up the url path. For example:
```python
es.post('tweets/tweet/', data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

Becomes:
```python
es.tweets.tweet.post(data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

Or using [] notation.  This can be useful for characters that are not allowed in python attributes:
```python
es['tweets']['tweet'].post(data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

More examples:

Searching tweets index for documents of type tweets
```python
es.tweets.tweet._search.get(data={'query' : {'match_all' : {} }})
```

Searching tweets and blogs index for documents of any type using a JSON strings
```python
es['tweets,blogs']._search.get(data='{"query" : {"match_all" : {}}}')
```

Thrift support
--------------
Before thrift will work with rawes, you must install the thrift python module
```bash
$ pip install thrift
```

By default, connections on ports between 9500 and 9600 will use thrift
```python
import rawes
es_thrift = rawes.Elastic('localhost:9500')
```

If you are using thrift on a non standard port, specify connection_type='thrift' as a parameter
```python
import rawes
es_thrift = rawes.Elastic('localhost:8500', connection_type='thrift')
```

Run Unit Tests
--------------
rawes' unit tests require the python thrift module to run:
```bash
$ pip install thrift
```

Run tests:
```bash
$ python -m unittest tests
```

Contact
-------
[@dwnoble](https://twitter.com/dwnoble)
