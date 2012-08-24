rawes
=====

About
-----
rawes is an elasticsearch driver for Python.  It provides a clean interface that is just a small wrapper on top of the native interface to elasticsearch.

Usage
-----

> import rawes
> es = rawes.Connection('localhost:9200')
> es.put()
> es.put()
> es.put()
> es.get()

:: Lets you do date strings or Date() objects.


Why rawes?
----------
elasticsearch's has a great native API, and I don't think there needs to be much abstraction on top of it.

Features
--------
* Thrift support

Run Unit Tests
--------------
python -m unittest tests

Contact
-------
@dwnoble
