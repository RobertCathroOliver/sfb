from django.db import models
from sfb import core

class LocationField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4
        super(LocationField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'char(4)'

    def to_python(self, value):
        if isinstance(value, core.Location):
            return value

        args = re.findall(r'\d{2}', value)
        return core.Location(*[int(a) for a in args])

    def get_db_prep_value(self, value):
        return str(value)

    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return [self.get_db_prep_value(value)]
        elif lookup_type == 'in':
            return [self.get_db_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

