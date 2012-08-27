rawes
=====

About
-----
rawes is an elasticsearch driver for Python.  It provides a small level of abstraction above the requests library - just enough to be useful, but not enough to obscure elasticsearch's great [native api](http://www.elasticsearch.org/guide/reference/api/)

Features
--------
* elasticsearch native API support
* gzip over HTTP support
* Thrift support

Usage
-----
Create a connection to elasticsearch
<pre><code>
import rawes
es = rawes.Elastic('localhost:9200')
</pre></code>

Create a new document in the twitter index of type tweet with id 1
<pre><code>
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
</pre></code>

Search for a document
<pre><code>
es.get('tweets/tweet/_search', data={
    'query' : {
        'match_all' : {}
    }
})
</pre></code>

Search for a document with a JSON string
<pre><code>
es.get('tweets,blogs/_search', data="""
{
    "query" : {
        "match_all" : {}
    }
}
""")
</pre></code>

Update a document
<pre><code>
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
</pre></code>

Delete a document
<pre><code>
es.delete('tweets/tweet/1')
</pre></code>


Alternate Syntax
----------------
<pre><code>
import rawes
es = rawes.Elastic('localhost:9200')
</pre></code>

Searching tweets index for documents of type tweets
<pre><code>
es.tweets.tweet._search.get(data={'query' : {'match_all' : {} }})
</pre></code>

Searching tweets and blogs index for documents of any type using a JSON strings
<pre><code>
es['tweets,blogs']._search.get(data='{"query" : {"match_all" : {}}}')
</pre></code>

Thrift support
--------------
Before thrift will work with rawes, you must install the thrift python module
<pre><code>
$ pip install thrift
</pre></code>

<pre><code>
import rawes
# By default, connections on ports between 9500 and 9600 will use thrift
es = rawes.Elastic('localhost:9500')
# If you are using thrift on a non standard port, specify connection_type='thrift' as a parameter
es2 = rawes.Elastic('localhost:8500', connection_type='thrift')
</pre></code>

Run Unit Tests
--------------
<pre><code>
$ python -m unittest tests
</pre></code>

Contact
-------
[@dwnoble](https://twitter.com/dwnoble)
