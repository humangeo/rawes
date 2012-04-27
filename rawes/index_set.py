from type_set import TypeSet

class IndexSet(object):
    """docstring for IndexSet"""
    def __init__(self, indices, elastic):
        self.indices = indices
        self.elastic = elastic
        self.base_path = indices if type(indices) == str else ','.join(indices)
    
    def __getitem__(self, types):
        """docstring for __getitem__"""
        return TypeSet(types=types, indices=self.indices, elastic=self.elastic)
    
    def delete_index(self):
        """Deletes the current index"""
        self.elastic.delete(self.base_path)
    
    def create_index(self, data=None):
        """Creates the current index"""
        self.elastic.put(self.base_path, data=data)