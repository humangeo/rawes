RawES
=====

About
-----
RawES is an elasticsearch driver for Python.  It provides a clean interface that is just a small wrapper on top of the native HTTP/Thrift interfaces to elasticsearch.

Usage
-----

> import rawes
> es = rawes.Connection('localhost:9200')
> es.put()
> es.put()
> es.put()
> es.get()

:: Lets you do date strings or Date() objects.


Run Unit Tests
--------------
python -m unittest tests

Contact
-------
@dwnoble