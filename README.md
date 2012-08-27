rawes
=====

About
-----
rawes is an elasticsearch driver for Python.  It provides a small level of abstraction above the requests library - just enough to be useful, but not enough to obscure elasticsearch's great [native api](http://www.elasticsearch.org/guide/reference/api/)

Features
--------
* Direct access to elasticsearch's native API
* Thrift support

Usage
-----
> import rawes
> es = rawes.Connection('localhost:9200')

# Searching 
> es.get('_search', data= {'query' : {'match_all' : True }})

# Searching with JSON strings
> es.get('_search', data= '{"query" : {"match_all" : true}}')


Thrift support
--------------
> import rawes
> # By default, connections on ports between 9500 and 9600 will use thrift
> es = rawes.Connection('localhost:9500')
> # If you are using thrift on a non standard port, specify connection_type='thrift' as a parameter
> es = rawes.Connection('localhost:8500', connection_type='thrift')

Run Unit Tests
--------------
python -m unittest tests

Contact
-------
@dwnoble
