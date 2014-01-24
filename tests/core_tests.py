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

import mock
import rawes
from rawes.elastic_exception import ElasticException
from tests import test_encoder
import unittest
from tests import config
import json
from datetime import datetime
import pytz
from pytz import timezone
import time

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
        self.custom_json_decoder = test_encoder.DateAwareJsonDecoder().decode
        #self.es_http_es_w_decoder = rawes.Elastic(url=self.http_url,)
        if not config.HTTP_ONLY:
            self.thrift_url = '%s:%s' % (config.ES_HOST, config.ES_THRIFT_PORT)
            self.es_thrift = rawes.Elastic(url=self.thrift_url)

    def test_http(self):
        self._reset_indices(self.es_http)
        self._test_document_search(self.es_http)
        self._test_document_update(self.es_http)
        self._test_document_delete(self.es_http)
        self._test_bulk_load(self.es_http)
        self._test_datetime_encoder(self.es_http)
        self._test_no_handler_found_for_uri(self.es_http)

    def test_thrift(self):
        if config.HTTP_ONLY:
            return
        self._reset_indices(self.es_thrift)
        self._test_document_search(self.es_thrift)
        self._test_document_update(self.es_thrift)
        self._test_document_delete(self.es_thrift)
        self._test_bulk_load(self.es_thrift)
        self._test_datetime_encoder(self.es_thrift)
        self._test_no_handler_found_for_uri(self.es_thrift)

    def test_timeouts(self):
        es_http_short_timeout = rawes.Elastic(url=self.http_url,timeout=0.0001)
        self._test_timeout(es_short_timeout=es_http_short_timeout)

        if not config.HTTP_ONLY:
            es_thrift_short_timeout = rawes.Elastic(url=self.thrift_url,timeout=0.0001)
            self._test_timeout(es_short_timeout=es_thrift_short_timeout)

    def test_json_decoder_encoder(self):
        es_http_decoder = rawes.Elastic(url=self.http_url,json_decoder=self.custom_json_decoder)
        es_http_encoder = rawes.Elastic(url=self.http_url,json_encoder=test_encoder.encode_custom)
        self._test_custom_encoder(self.es_http,es_encoder=es_http_encoder)
        self._test_custom_decoder(self.es_http,es_decoder=es_http_decoder)
        if not config.HTTP_ONLY:
            self._reset_indices(self.es_thrift)
            self._wait_for_good_health(self.es_thrift)
            es_thrift_decoder = rawes.Elastic(url=self.thrift_url,json_decoder=self.custom_json_decoder)
            es_thrift_encoder = rawes.Elastic(url=self.thrift_url,json_encoder=test_encoder.encode_custom)
            self._test_custom_encoder(self.es_thrift,es_encoder=es_thrift_encoder)
            self._test_custom_decoder(self.es_thrift,es_decoder=es_thrift_decoder)

    def test_empty_constructor(self):
        with mock.patch('rawes.http_connection.HttpConnection.__init__',
                mock.MagicMock(return_value=None)) as new_connection:
            rawes.Elastic()
            new_connection.assert_called_with('http://localhost:9200',
                                              timeout=30)

    def test_https(self):
        with mock.patch('rawes.http_connection.HttpConnection.__init__',
                mock.MagicMock(return_value=None)) as new_connection:
            rawes.Elastic("https://localhost")
            new_connection.assert_called_with('https://localhost:443',
                                              timeout=30)

    def _reset_indices(self, es):
        # If the index does not exist, test creating it and deleting it
        try:
            index_status_result = es.get('%s/_status' % config.ES_INDEX)
        except ElasticException:
            create_index_result = es.put(config.ES_INDEX)

        # Test deleting the index
        delete_index_result = es.delete(config.ES_INDEX)
        try:
            es.get('%s/_status' % config.ES_INDEX)['status']
            self.assertTrue(False)
        except ElasticException as e:
            self.assertTrue(e.status_code == 404)

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
        self._wait_for_good_health(es)
        try:
            search_result = es[config.ES_INDEX].sometype['123'].get()
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

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
        try:
            search_result = es[config.ES_INDEX].persontype['555'].get()
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

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
        try:
            search_result = es[config.ES_INDEX]['persontype']['555'].get()
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

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

        self.assertEqual(index_size + 3, new_index_size)

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

        self.assertEqual(index_size + 6, newer_index_size)

    def _test_datetime_encoder(self, es):
        # Ensure the document does not already exist
        test_type = 'datetimetesttype'
        test_id = 123

        try:
            search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

        # Ensure no mapping exists for this type
        try:
            mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

        # Create a sample document with a datetime
        eastern_timezone = timezone('US/Eastern')
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
        time.sleep(0.5) # Wait for the mapping to exist.  Probably a better way to do this
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))

        if test_type not in mapping:
            raise(Exception('type %s not in mapping: %r' % (test_type,mapping)))
        mapping_date_format = mapping[test_type]['properties']['updated']['format']
        self.assertEqual(mapping_date_format,'dateOptionalTime')

        # Verify the document was created and has the proper date
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue('exists' in search_result and search_result['exists'])
        self.assertEqual('2012-11-12T14:30:03Z',search_result['_source']['updated'])

    def _test_custom_encoder(self, es, es_encoder):
        # Ensure the document does not already exist
        test_type = 'customdatetimetesttype'
        test_id = 456
        try:
            search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertTrue(e.status_code >= 404)

        # Ensure no mapping exists for this type
        try:
            mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

        # Create a sample document with a datetime
        eastern_timezone = timezone('US/Eastern')
        test_updated = datetime(2012, 11, 12, 9, 30, 3, tzinfo=eastern_timezone)
        insert_result = es.put('%s/%s/%s' % (config.ES_INDEX, test_type, test_id), data={
            'name': 'dateme',
            'updated' : test_updated
        }, params={
            'refresh': 'true'
        }, json_encoder=test_encoder.encode_custom)
        self.assertTrue(insert_result['ok'])

        # Flush the index after adding the new item to ensure the mapping is updated
        refresh_result = es.post('%s/_refresh' % config.ES_INDEX)
        self.assertTrue(refresh_result['ok'])

        # Verify the mapping was created properly
        mapping = es.get('%s/%s/_mapping' % (config.ES_INDEX, test_type))
        mapping_date_format = mapping[test_type]['properties']['updated']['format']
        self.assertEqual(mapping_date_format,'dateOptionalTime')

        # Verify the document was created and has the proper date
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result['exists'])
        self.assertEqual('2012-11-12',search_result['_source']['updated'])

        # Ensure that the class level encoder works
        # Encode a new doc w class encoder
        encoded_test_id = 12412545
        encoded_insert_result = es_encoder.put('%s/%s/%s' % (config.ES_INDEX, test_type, encoded_test_id), data={
            'name': 'dateme',
            'updated' : test_updated
        }, params={
            'refresh': 'true'
        })
        encoded_search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, encoded_test_id))
        self.assertTrue(encoded_search_result['exists'])
        self.assertEqual('2012-11-12',encoded_search_result['_source']['updated'])

    def _test_custom_decoder(self,es, es_decoder):
        # Ensure the document does not already exist
        test_type = 'customdecodertype'
        test_id = 889988
        try:
            search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,404)

        # Create a sample document with a value %Y-%m-%d
        insert_result = es.put('%s/%s/%s' % (config.ES_INDEX, test_type, test_id), data={
            'name': 'testdecode',
            'updated' : "2013-07-04"
        }, params={
            'refresh': 'true'
        })
        self.assertTrue(insert_result['ok'])

        # Flush the index after adding the new item to ensure the mapping is updated
        refresh_result = es.post('%s/_refresh' % config.ES_INDEX)
        self.assertTrue(refresh_result['ok'])

        # Ensure the document was created
        search_result = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result['exists'])
        self.assertEqual('2013-07-04',search_result['_source']['updated'])

        # Ensure the class level json decoder works
        search_result_constructor_decoded = es_decoder.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id))
        self.assertTrue(search_result_constructor_decoded['exists'])
        self.assertEqual(type(search_result_constructor_decoded['_source']['updated']),datetime)
        self.assertEqual(search_result_constructor_decoded['_source']['updated'].year, 2013)
        self.assertEqual(search_result_constructor_decoded['_source']['updated'].month, 07)
        self.assertEqual(search_result_constructor_decoded['_source']['updated'].day, 04)
        self.assertEqual(search_result_constructor_decoded['_source']['updated'].tzinfo, pytz.utc)

        # Ensure the request level json decoder works
        search_result_decoded = es.get('%s/%s/%s' % (config.ES_INDEX, test_type, test_id),json_decoder=self.custom_json_decoder)
        self.assertTrue(search_result_decoded['exists'])
        self.assertEqual(type(search_result_decoded['_source']['updated']), datetime)
        self.assertEqual(search_result_decoded['_source']['updated'].year, 2013)
        self.assertEqual(search_result_decoded['_source']['updated'].month, 07)
        self.assertEqual(search_result_decoded['_source']['updated'].day, 04)
        self.assertEqual(search_result_decoded['_source']['updated'].tzinfo, pytz.utc)

    def _test_timeout(self,es_short_timeout):
        timed_out = False
        try:
            result = es_short_timeout.get("/_mapping")
        except Exception as e:
            timed_out = str("{0}".format(e)).find('timed out') > -1
        self.assertTrue(timed_out)

    def _test_no_handler_found_for_uri(self,es):
        try:
            es[config.ES_INDEX].nopedontexist.get()
            self.fail("Document should not exist")
        except ElasticException as e:
            self.assertEqual(e.status_code,400)

    def _wait_for_good_health(self,es):
        # Give elasticsearch a few seconds to turn 'yellow' or 'green' after an operation
        # Try 6 times
        interval = 0.25
        good_health = False
        for i in range(5):
            health = es.get("_cluster/health")
            if health["status"] == "green" or health["status"] == "yellow":
                good_health = True
                break
            time.sleep(interval)
        self.assertTrue(good_health)

