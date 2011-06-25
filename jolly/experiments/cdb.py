"""CouchDB persistence

To save:
 convert the obj into a representation based on primitive python data types
 store the obj and return its id

To restore:
 retrieve the obj as primitives based on id
 convert the retrieved document to an object

database objects:
users
games
command queues

"""



class Db(object):

    def __init__(self):
        self.doc_id_cache = {}
        self.obj_cache = {}

    def store(self, obj):
        doc_id = self.get_doc_id(obj)
        doc = self.deconstruct(obj)
        self.db[doc_id] = doc
        self.doc_id_cache[id(obj)] = doc_id
        self.obj_cache[doc_id] = obj
        return doc_id

    def restore(self, doc_id):
        if doc_id in self.obj_cache:
            return self.obj_cache[doc_id]
        doc = self.db[doc_id]
        obj = self.construct(doc)
        self.obj_cache[doc_id] = obj
        return obj

    def get_doc_id(self, obj):
        return self.doc_id_cache.get(id(obj), self.gen_doc_id())

    def gen_doc_id():
        pass

    def deconstruct(self, obj):
        pass

    def construct(self, doc):
        pass
