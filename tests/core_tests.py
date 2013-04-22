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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rawes
from rawes.elastic_exception import ElasticException
from tests import test_encoder
import unittest
import config
import json
from datetime import datetime
from dateutil import tz


import logging
log_level = logging.ERROR
log_format = '[%(levelname)s] [%(name)s] %(asctime)s - %(message)s'
logging.basicConfig(format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p', level=log_level)
soh = logging.StreamHandler(sys.stdout)
soh.setLevel(log_level)
logger = logging.getLogger("rawes.tests")
logger.addHandler(soh)


class TestElasticCore(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.http_url = '%s:%s' % (config.ES_HOST, config.ES_HTTP_PORT)
        self.es_http = rawes.Elastic(url=self.http_url)
        self.thrift_url = '%s:%s' % (config.ES_HOST, config.ES_THRIFT_PORT)
        self.es_thrift = rawes.Elastic(url=self.thrift_url)
        

    def test_http(self):
        self._reset_indices(self.es_http)
        self._test_document_search(self.es_http)
        self._test_document_update(self.es_http)
        self._test_document_delete(self.es_http)
        self._test_bulk_load(self.es_http)
        self._test_datetime_encoder(self.es_http)
        self._test_custom_encoder(self.es_http)

    def test_thrift(self):
        self._reset_indices(self.es_thrift)
        self._test_document_search(self.es_thrift)
        self._test_document_update(self.es_thrift)
        self._test_document_delete(self.es_thrift)
        self._test_bulk_load(self.es_thrift)
        self._test_datetime_encoder(self.es_thrift)
        self._test_custom_encoder(self.es_thrift)
        

    def test_except_on_error(self):
        es_http_except_on_error = rawes.Elastic(url=self.http_url,except_on_error=True)
        es_thrift_except_on_error = rawes.Elastic(url=self.thrift_url,except_on_error=True)
        self._test_except_on_error(self.es_http, es_http_except_on_error)
        self._test_except_on_error(self.es_thrift, es_thrift_except_on_error)

    def test_timeouts(self):
        es_http_short_timeout = rawes.Elastic(url=self.http_url,timeout=0.0001)
        es_thrift_short_timeout = rawes.Elastic(url=self.thrift_url,timeout=0.0001)
        self._test_timeout(es_short_timeout=es_http_short_timeout)
        self._test_timeout(es_short_timeout=es_thrift_short_timeout)


    def test_empty_constructor(self):
        es = rawes.Elastic()
        self.assertEquals(es.url.scheme, "http")
        self.assertEquals(es.url.hostname, "localhost")
        self.assertEquals(es.url.port, 9200)
    
    def test_https(self):
        es = rawes.Elastic("https://localhost")
        self.assertEquals(es.url.scheme, "https")
        self.assertEquals(es.url.port, 443)

    def _reset_indices(self, es):
        # If the index does not exist, test creating it and deleting it
        index_status_result = es.get('%s/_status' % config.ES_INDEX)
        if 'status' in index_status_result and index_status_result['status'] == 404:
            create_index_result = es.put(config.ES_INDEX)

        # Test deleting the index
        delete_index_result = es.delete(config.ES_INDEX)
        index_deleted = es.get('%s/_status' % config.ES_INDEX)['status'] == 404
        self.assertTrue(index_deleted)

        # Now remake the index
        es.put(config.ES_INDEX)
        index_exists = es.get('%s/_status' % config.ES_INDEX)['ok'] == True
        self.assertTrue(index_exists)

    def _test_document_search(self, es):
        # Create some sample documents
        result1 = es.post('%s/tweet/' % config.ES_INDEX, data={
            'user': 'dwnoble',
            'post_date': '2012-8-27T08:00:30Z',
            'message': 'Tweeting about elasticsearch'
        }, params={
            'refresh': True
        })
        self.assertTrue(result1['ok'])
        result2 = es.put('%s/post/2' % config.ES_INDEX, data={
            'user': 'dan',
            'post_date': '2012-8-27T09:30:03Z',
            'title': 'Elasticsearch',
            'body': 'Blogging about elasticsearch'
        }, params={
            'refresh': 'true'
        })
        self.assertTrue(result2['ok'])

        # Search for documents of one type
        search_result = es.get('%s/tweet/_search' % config.ES_INDEX, data={
            'query': {
                'match_all': {}
            }
        }, params={
            'size': 2
        })
        self.assertTrue(search_result['hits']['total'] == 1)

        # Search for documents of both types
        search_result2 = es.get('%s/tweet,post/_search' % config.ES_INDEX, data={
            'query': {
                'match_all': {}
            }
        }, params={
            'size': '2'
        })
        self.assertTrue(search_result2['hits']['total'] == 2)

    def _test_document_update(self, es):
        # Ensure the document does not already exist (using alternate syntax)
        search_result = es[config.ES_INDEX].sometype['123'].get()
        self.assertFalse(search_result['exists'])

        # Create a sample document (using alternate syntax)
        insert_result = es[config.ES_INDEX].sometype[123].put(data={
            'value': 100,
            'other': 'stuff'
        }, params={
            'refresh': 'true'
        })
        self.assertTrue(insert_result['ok'])

        # Perform a simple update (using alternate syntax)
        update_result = es[config.ES_INDEX].sometype['123']._update.post(data={
            'script': 'ctx._source.value += value',
            'params': {
                'value': 50
            }
        }, params={
            'refresh': 'true'
        })
        self.assertTrue(update_result['ok'])

        # Ensure the value was updated
        search_result2 = es[config.ES_INDEX].sometype['123'].get()
        self.assertTrue(search_result2['_source']['value'] == 150)

    def _test_document_delete(self, es):
        # Ensure the document does not already exist (using alternate syntax)
        search_result = es[config.ES_INDEX].persontype['555'].get()
        self.assertFalse(search_result['exists'])

        # Create a sample document (using alternate syntax)
        insert_result = es[config.ES_INDEX].persontype[555].put(data={
            'name': 'bob'
        }, params={
            'refresh': 'true'
        })
        self.assertTrue(insert_result['ok'])

        # Delete the document
        delete_result = es[config.ES_INDEX].delete('persontype/555')
        self.assertTrue(delete_result['ok'])

        # Verify the document was deleted
        search_result = es[config.ES_INDEX]['persontype']['555'].get()
        self.assertFalse(search_result['exists'])

    def _test_bulk_load(self, es):
        index_size = es[config.ES_INDEX][config.ES_TYPE].get('_search',params={'size':0})['hits']['total']

        bulk_body = '''
        {"index" : {}}
        {"key":"value1"}
        {"index" : {}}
        {"key":"value2"}
        {"index" : {}}
        {"key":"value3"}
        '''

        es[config.ES_INDEX][config.ES_TYPE].post('_bulk', data = bulk_body, params={
            'refresh': 'true'
        })
        new_index_size = es[config.ES_INDEX][config.ES_TYPE].get('_search',params={'size':0})['hits']['total']

        self.assertEquals(index_size + 3, new_index_size)

        bulk_list = [
            {"index" : {}},
            {"key":"value4"},
            {"index" : {}},
            {"key":"value5"},
            {"index" : {}},
            {"key":"value6"}
        ]

        bulk_body_2 = '\n'.join(map(json.dumps, bulk_list))+'\n'
        es[config.ES_INDEX][config.ES_TYPE].post('_bulk', data = bulk_body_2, params={
            'refresh': 'true'
        })
        newer_index_size = es[config.ES_INDEX][config.ES_TYPE].get('_search',params={'size':0})['hits']['total']

        self.assertEquals(index_size + 6, newer_index_size)

    def _test_datetime_encoder(self, es):
        # Ensure the document does not already exist
        test_type = 'datetimetesttype'
        test_id = 123
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertFalse(search_result['exists'])

        # Ensure no mapping exists for this type
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
        self.assertEquals(mapping['status'], 404)

        # Create a sample document with a datetime
        eastern_timezone = tz.gettz('America/New_York')
        test_updated = datetime(2012, 11, 12, 9, 30, 3, tzinfo=eastern_timezone)
        insert_result = es.put('%s/%s/%s' % (config.ES_INDEX, test_type, test_id), data={
            'name': 'dateme',
            'updated' : test_updated
        })
        self.assertTrue(insert_result['ok'])

        # Refresh the index after setting the mapping
        refresh_result = es.post('%s/_refresh' % config.ES_INDEX)
        self.assertTrue(refresh_result['ok'])

        # Verify the mapping was created properly
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
        if test_type not in mapping:
            raise(Exception('testy.... : %r' % mapping))
        mapping_date_format = mapping[test_type]['properties']['updated']['format']
        self.assertEquals(mapping_date_format,'dateOptionalTime')

        # Verify the document was created and has the proper date
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result['exists'])
        self.assertEquals('2012-11-12T14:30:03Z',search_result['_source']['updated'])

    def _test_custom_encoder(self, es):
        # Ensure the document does not already exist
        test_type = 'customdatetimetesttype'
        test_id = 456
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertFalse(search_result['exists'])

        # Ensure no mapping exists for this type
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
        self.assertEquals(mapping['status'], 404)

        # Create a sample document with a datetime
        eastern_timezone = tz.gettz('America/New_York')
        test_updated = datetime(2012, 11, 12, 9, 30, 3, tzinfo=eastern_timezone)
        insert_result = es.put('%s/%s/%s' % (config.ES_INDEX, test_type, test_id), data={
            'name': 'dateme',
            'updated' : test_updated
        }, params={
            'refresh': 'true'
        }, json_encoder=test_encoder.encode_custom)
        self.assertTrue(insert_result['ok'])

        # Flush the index after adding the new item to ensure the mapping is updated
        refresh_result = es.post('%s/_flush' % config.ES_INDEX)
        self.assertTrue(refresh_result['ok'])

        # Verify the mapping was created properly
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
        mapping_date_format = mapping[test_type]['properties']['updated']['format']
        self.assertEquals(mapping_date_format,'dateOptionalTime')

        # Verify the document was created and has the proper date
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result['exists'])
        self.assertEquals('2012-11-12',search_result['_source']['updated'])

    def _test_except_on_error(self, es, es_except_on_error):
        # Make a new document
        # Create some sample documents
        test_type = 'test_exceptions'
        test_id = 56789
        result = es.post('%s/%s/%s' % (config.ES_INDEX, test_type, test_id), data={
            'data': 'test_errors'
        }, params={
            'refresh': True
        })

        # Get the document with the normal es instance
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result['exists'])

        # Now get the document with the es instance that throws exception on errors (No exception should be thrown)
        search_result_2 = es_except_on_error.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result_2['exists'])

        # Try getting a document that doesn't exist from the normal es instance
        fake_id = 124098124
        search_result_3= es.get('%s/%s/%s' % (config.ES_INDEX, test_type, fake_id))
        self.assertFalse(search_result_3['exists'])

        # Now try getting a document that doesn't exist where we raise exceptions on error (this time an exception should be thrown)
        fake_id = 124098124
        exception_thrown = False
        try:
            search_result_4= es_except_on_error.get('%s/%s/%s' % (config.ES_INDEX, test_type, fake_id))   
        except ElasticException as e:
            result = e.result 
            status_code = e.status_code
            self.assertFalse(result['exists'])
            self.assertEquals(status_code,404)
            exception_thrown = True        
        self.assertTrue(exception_thrown)

    def _test_timeout(self,es_short_timeout):
        timed_out = False
        try:
            result = es_short_timeout.get("/_mapping")
        except Exception as e:
            timed_out = str(e.message).find('timed out') > -1
        self.assertTrue(timed_out)


