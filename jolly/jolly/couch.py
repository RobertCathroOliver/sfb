import jolly.util

class Database(object):

    def __init__(self, settings):
        from couchdb.client import Server
        server = Server()
        self.db = server[settings.DATABASE['NAME']]
        self.identifier = jolly.util.import_object(settings.IDENTIFIER)
        self.registry = jolly.util.import_object(settings.REGISTRY)
        self.value_resolver = jolly.util.import_object(settings.VALUE_RESOLVER)
        self.decoders = jolly.util.import_object(settings.DATABASE['DECODERS'])(settings, self)
        self.encoders = jolly.util.import_object(settings.DATABASE['ENCODERS'])(settings)
        self.references = None

        self.revs = {}
        self.dirty_objs = set()
        self.uninitialized_objs = {}

    def dirty(self, obj):
        """Mark the object as dirty so it will be stored in the database."""
        doc_id = self.identifier.get_obj_id(obj)
        self.dirty_objs.add(doc_id)

    def dirty_all(self):
        """Mark all stored objects as dirty."""
        for obj in self.identifier.obj_cache:
            self.dirty(obj)

    def store(self, obj):
        """Store the object in the database."""
        import jolly.json_encode
        doc_id = self.identifier.get_obj_id(obj)

        # if the object hasn't changed, do nothing
        if doc_id in self.identifier.obj_cache and not doc_id in self.dirty_objs:
            return doc_id

        # convert the object to its database representation
        doc = jolly.json_encode.encode(obj, self.encoders)

        # maintain the correct _rev to avoid update conflicts
        rev = self.get_doc_rev(doc_id)
        if rev:
            doc['_rev'] = rev

        # actually store the document in the database
        self.db[doc_id] = doc

        # update the caches
        self.identifier.set_obj_id(obj, doc_id)
        if doc_id in self.dirty_objs:
             self.dirty_objs.remove(doc_id)

        return doc_id

    def restore(self, doc_id):
       """Retrieve the document identified by doc_id from the database."""
       obj = self.get_obj(doc_id)
       if obj is None or doc_id in self.dirty_objs:
            doc = dict(self.db[doc_id])
            self.revs[doc_id] = doc['_rev']
            obj = self.decode(doc)
       return obj

    def restore_view(self, name, filter=None):
        """Restore a view from the database."""
        if filter:
            view_results = self.db.view(name, key=filter)
        else:
            view_results = self.db.view(name)

        result = []
        for row in view_results:
            obj = self.get_obj(row.id)
            if obj is None or row.id in self.dirty_objs:
                 doc = dict(row.value)
                 self.revs[row.id] = doc['_rev']
                 obj = self.decode(doc)
            result.append(obj)
        return result
            
    
    def decode(self, doc, references=None):
        """Convert a JSON document to Python object."""
        if references is None:
            references = self.get_references(doc)

        if isinstance(doc, list):
            return [self.decode(v, references) for v in doc]
        elif isinstance(doc, dict):
            if '$lookup' in doc:
                return self.registry.get(doc['$lookup'])
            if '$class' in doc:
                if '_id' in doc:
                    obj = self.get_obj(doc['_id'])
                    # if doc has already been decoded
                    if not obj is None:
                        return obj
                # decode docs to classes
                return self.decoders[doc['$class']](doc, references)
            # regular dicts
            return dict((k, self.decode(v, references)) for k, v in doc.items() if not k[0] in '_$')
        elif self.is_uuid(doc):
            return self._get_obj(doc, references)
        else:
            return self.value_resolver.resolve(doc)

    def get_obj(self, doc_id):
        """Return a completed object by doc_id."""
        return self.identifier.get_obj(doc_id)

    def set_obj(self, doc_id, obj):
        """Assign a complete object to a doc_id."""
        self.identifier.set_obj_id(obj, doc_id)

    def _get_obj(self, doc_id, references):
        """Retrieve a document from cache or by decoding."""
        obj = self.get_obj(doc_id)
        if not obj is None:
            return obj
        if doc_id in references:
            return references[doc_id]
        return self.restore(doc_id)

    def get_doc_rev(self, doc_id):
        """Return the document revision number."""
        return self.revs.get(doc_id)

    def get_references(self, doc):
        """Return a map of doc_ids to empty objects of the proper class."""
        references = {}
        if isinstance(doc, list):
            for v in doc:
                references.update(self.get_references(v))
        elif isinstance(doc, dict):
            if '_id' in doc:
                _class = jolly.util.import_object(doc['$class'])
                obj = _class.__new__(_class)
                references[doc['_id']] = obj
            for v in doc.values():
                references.update(self.get_references(v))
        return references

    def is_uuid(self, value):
        """Determine whether a value is a UUID."""
        import uuid
        try:
            uuid.UUID(hex=value)
        except (AttributeError, ValueError, TypeError):
            return False
        return True
