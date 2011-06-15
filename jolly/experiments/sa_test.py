from sqlalchemy import Column, Integer, String, Table, create_engine
from sqlalchemy import orm, MetaData, Column, ForeignKey 
from sqlalchemy.orm import relation, mapper, sessionmaker, relationship
from sqlalchemy.orm.collections import column_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

engine = create_engine('sqlite:///:memory:', echo=True)
meta = MetaData(bind=engine)

tb_systems = Table('systems', meta, 
        Column('id', Integer, primary_key=True), 
        Column('name', String(20)),
    )
tb_properties = Table('properties', meta, 
        Column('system_id', Integer, ForeignKey('systems.id'), primary_key=True),
        Column('value1', String(20)),
        Column('value2', String(20)),
        Column('value3', Integer)
    )
tb_foos = Table('foos', meta,
	Column('id', Integer, primary_key=True),
	Column('slide_id', Integer, ForeignKey('properties.system_id')),
	Column('position', Integer),
	Column('value', Integer))

class PropertyMap(dict):
    def __init__(self, properties):
	self.update(properties)
    def __getattr__(self, name):
	try:
	    return self[self.unsanitize(name)]
	except KeyError:
	    raise AttributeError(name)
    def __setattr__(self, name, value):
	try:
	    self[self.sanitize(name)] = value
	except KeyError:
	    raise AttributeError(name)
    def sanitize(self, name):
	return 'p_{0}'.format(name.replace('-', '_'))
    def unsanitize(self, name):
	return name.replace('_', '-')[2:]

class Foo(object):
    def __init__(self, value):
	self.value = value

    def __str__(self):
	return str(self.value)

    def __repr__(self):
	return 'Foo({0})'.format(self.value)

class SystemPropertyDict(object):

    def __init__(self, properties):
	self.__dict__.update(properties)

    def __setitem__(self, name, value):
	self.__dict__[name] = value

    def __getitem__(self, name):
	return self.__dict__[name]


class System(object):
    def __init__(self, name, properties):
	self.name = name
	self.properties = properties

mapper(Foo, tb_foos)
mapper(SystemPropertyDict, tb_properties, properties={
    'foos': relationship(Foo, collection_class=ordering_list('position'),
	                      order_by=[tb_foos.c.position])})
mapper(System, tb_systems, properties={
        'properties': relationship(SystemPropertyDict, uselist=False)
    })

meta.create_all()
Session = sessionmaker(bind=engine)
s = Session()

