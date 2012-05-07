from type_set import TypeSet
import query_helpers

class IndexSet(object):
    """docstring for IndexSet"""
    def __init__(self, indices, elastic):
        self.indices = indices
        self.elastic = elastic
        self.base_path = indices if type(indices) == str else ','.join(indices)
    
    def __getitem__(self, types):
        """docstring for __getitem__"""
        return TypeSet(types=types, indices=self.indices, elastic=self.elastic)
    
    def search(self, data, params={}):
        """Search for a document"""
        params['timeout'] = params['timeout'] if params.has_key('timeout') else self.elastic.timeout
        query_string = query_helpers.build_query_string(params)
        path = '%s/_search%s' % (self.base_path, query_string)
        response = self.elastic.get(path,data=data)
        return response
    
    def delete_index(self):
        """Deletes the current index"""
        self.elastic.delete(self.base_path)
    
    def create_index(self, data=None):
        """Creates the current index"""
        self.elastic.put(self.base_path, data=data)