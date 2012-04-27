#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rawes
import unittest
import config

class TestElasticCore(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        http_url = '%s:%s' % (config.ES_HOST, config.ES_HTTP_PORT)
        self.elastic = rawes.Elastic(url=http_url)
        self.elastic_index = self.elastic[config.ES_INDEX]
        self.elastic_type = self.elastic[config.ES_INDEX][config.ES_TYPE]
        self.elastic_index.delete_index()
        self.elastic_index.create_index()
    
    def test_index(self):
        """docstring for test_index"""
        # test create with id
        doc1 = {'name' : 'Test Index'}
        doc1_id = 'test_index_1'
        self.assertFalse(self._exists(doc1_id))
        result = self.elastic_type.index(data=doc1, _id=doc1_id)
        self.assertTrue(result['ok'])
        self.assertTrue(self._exists(doc1_id))
        
        # test create without id
        
        # test create with a parameter
        pass
    
    def test_delete(self):
        """docstring for test_delete"""
        # Create a new document
        doc = {'name' : 'Test Delete'}
        result = self.elastic_type.index(data=doc)
        doc_id = result['_id']
        
        self.assertTrue(self._exists(doc_id)) # Make sure that document exists
        self.elastic_type.delete(_id=doc_id) # Delete the document
        self.assertFalse(self._exists(doc_id)) # Ensure it no longer exists
    
    def test_get(self):
        # Test basic get
        doc = {'name' : 'Test Get'}
        doc_id = 'test_get'
        self.assertFalse(self._exists(doc_id))
        self.elastic_type.index(data=doc, _id=doc_id)
        self.assertTrue(self._exists(doc_id))
        self.assertEquals(self.elastic_type.get(_id=doc_id)['_source']['name'], 'Test Get')
        
        # Test with params
        doc2 = {'field1' : 'val1', 'field2' : 'val2', 'field3' : 'val3'}
        doc2_id = 'test_get_2'
        self.assertFalse(self._exists(doc2_id))
        self.elastic_type.index(data=doc2, _id=doc2_id)
        doc2_retrieved = self.elastic_type.get(_id=doc2_id, params={'fields' : 'field1,field2'})
        self.assertTrue(doc2_retrieved['fields'].has_key('field1'))
        self.assertTrue(doc2_retrieved['fields'].has_key('field2'))
        self.assertFalse(doc2_retrieved['fields'].has_key('field3'))
    
    def test_multi_get(self):
        self.elastic_type.index(data={'name' : 'multi_get_doc1'}, _id='multi_get_doc1')
        self.elastic_type.index(data={'name' : 'multi_get_doc2'}, _id='multi_get_doc2')
        self.elastic_type.index(data={'name' : 'multi_get_doc3'}, _id='multi_get_doc3')
        
        multi_get_query = {
            "docs" : [
                {
                    "_id" : "multi_get_doc1"
                },
                {
                    "_id" : "multi_get_doc2"
                }
            ]
        }
        result = self.elastic_type.multi_get(data=multi_get_query)
        self.assertEquals(len(result['docs']),2)
    
    def _exists(self, _id):
        doc = self.elastic_type.get(_id=_id)
        return doc['exists']
