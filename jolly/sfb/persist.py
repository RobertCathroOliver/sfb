import sqlalchemy
import sqlalchemy.sql

column_types = {}
column_types[int] = sqlalchemy.Integer
column_types[str] = sqlalchemy.String
column_types[basestring] = sqlalchemy.String

def create_type(klass, serialize, deserialize, base_type=sqlalchemy.types.String):
    """Create an SQLAlchemy column type."""
    type_name = klass.__name__ + 'SQLAlchemy'
    def process_bind_param(self, value, dialect):
        return serialize(value)
    def process_result_value(self, value, dialect):
        return deserialize(value)
    class_dict = {'process_bind_param' : process_bind_param,
                  'process_result_value' : process_result_value,
                  'impl' : base_type}
    result = type(type_name, (sqlalchemy.types.TypeDecorator,), class_dict)
    return result

class System(object):
    """An SQLAlchemy persistance engine for systems."""

    def __init__(self, metadata, column_types):
	self.metadata = metadata
	self.column_types = column_types
	self.tables = {}
	self.prototypes = {}
	self._ids = {}
	self._system_table = None
       
    def load(self, connection, id_):
	"""Load a system from the database."""
	prototype = self.load_prototype(connection, id_)
	table = self.get_table(prototype)
	select = table.select(table.c.system_id==id_)
	row = connection.execute(select).fetchone()
	properties = dict((self.decode_property_name(k), v) 
		           for k, v in row.items() if k.startswith('p_'))
	params = [p for s in prototype.services for p in s.properties]
	for p in params:
	    if self.is_list_property(p):
		properties[p.name] = self.load_list_property(connection, id_, p)
	system = prototype.create_system(properties)
	self._ids[id(system)] = id_
	return system

    def load_prototype(self, connection, id_):
	select = sqlalchemy.sql.select([self.system_table.c.prototype],
		                        self.system_table.c.system_id==id_)
	name = connection.execute(select).fetchone()[0]
        return self.prototypes[name]

    def load_list_property(self, connection, id_, property):
	"""Return list property value from the database."""
	table = self.get_list_property_table(property)
	select = table.select(table.c.system_id==id_).order_by(table.c.priority)
	rows = connection.execute(select).fetchall()
	value = [r[self.encode_property_name(property.name)] for r in rows]
	return value

    def save(self, connection, system):
	"""Save a system to the database."""
        id_ = self._ids.get(id(system))

	transaction = connection.begin()
	try:
	    if id_:
		self.update_properties(connection, id_, system)
	    else:
		id_ = self.insert_system(connection, system)
		self.insert_properties(connection, id_, system)
		self._ids[id(system)] = id_
	    transaction.commit()
	except:
	    transaction.rollback()
	    raise

	return id_

    def insert_system(self, connection, system):
	"""Insert the system in the systems database table."""
        values = {'prototype': system.prototype.name}
	insert = self.system_table.insert().values(**values)
	result = connection.execute(insert)
	pk = result.inserted_primary_key[0]
	return pk

    def insert_properties(self, connection, id_, system):
	"""Insert the system properties in the database."""
	properties = [p for s in system.prototype.services for p in s.properties]
	values = self.get_property_values(system)
	values['system_id'] = id_
	for p in properties:
	    if self.is_list_property(p):
		key = self.encode_property_name(p.name)
		self.insert_list_property(connection, id_, p, values[key])
		del values[key]
	table = self.get_table(system.prototype)
	connection.execute(table.insert().values(**values))

    def insert_list_property(self, connection, id_, property, values):
	"""Insert list property values in the database."""
	if not values: return
	table = self.get_list_property_table(property)
	name = self.encode_property_name(property.name)
	pvalues = [{'system_id': id_, 'priority': i, name: v} for i, v in enumerate(values)]
	print pvalues
        for p in pvalues:
	    insert = table.insert().values(**p)
	    connection.execute(insert)

    def update_properties(self, connection, id_, system):
	"""Update the system properties in the database."""
	properties = [p for s in system.prototype.services for p in s.properties]
	values = self.get_property_values(system)
	for p in properties:
	    if self.is_list_property(p):
		key = self.encode_property_name(p.name)
		self.update_list_property(connection, id_, p, values[key])
		del values[key]
	table = self.get_table(system.prototype)
	connection.execute(table.update().values(**values).where(table.c.system_id==id_))

    def update_list_property(self, connection, id_, property, values):
	"""Update list property value in the database."""
	table = self.get_list_property_table(property)
	connection.execute(table.delete().where(table.c.system_id==id_))
	self.insert_list_property(connection, id_, property, values)

    def get_table(self, prototype):
	"""Return the table used to persist the given prototype."""
	if not prototype in self.tables:
	    self.tables[prototype] = self.prepare_table(prototype)
	    self.prototypes[prototype.name] = prototype
	return self.tables[prototype]

    @property
    def system_table(self):
	"""Return the table used to persist a System."""
	if self._system_table is None:
	    self._system_table = self.prepare_system_table()
	return self._system_table

    def get_list_property_table(self, property):
	"""Return the table used to persist the list property."""
	if not property in self.tables:
	    self.tables[property] = self.prepare_list_property(property)
	return self.tables[property]

    def prepare_table(self, prototype):
	"""Create a database table definition for storing a prototype."""
	table_name = 'system_{0}'.format(self.sanitize_name(prototype.name))
	columns = [self.prepare_foreign_key_column('systems', 'system_id')]
	properties = [p for s in prototype.services for p in s.properties]
	for p in properties:
	    if self.is_list_property(p):
		ptable = self.get_list_property_table(p)
	    else:
	        column = self.prepare_column(p.name, p.required_class, p.mandatory)
	        columns.append(column)
	table = sqlalchemy.Table(table_name, self.metadata, *columns)
	return table

    def prepare_system_table(self):
	"""Create the database table definition for storing a System."""
	columns = [sqlalchemy.Column('system_id', sqlalchemy.Integer,
	                             primary_key=True),
		   sqlalchemy.Column('prototype', sqlalchemy.String,
		                     nullable=False)]
        table = sqlalchemy.Table('systems', self.metadata, *columns)
	return table

    def is_list_property(self, property):
	"""Return whether a given property is a list."""
	return isinstance(property.required_class, list)

    def prepare_list_property(self, property):
	"""Create the necessary table to store a list property."""
	table_name = 'property_{0}'.format(self.sanitize_name(property.name))
	columns = [sqlalchemy.Column('id', sqlalchemy.Integer,
	                             primary_key=True),
		   self.prepare_foreign_key_column('systems', 'system_id', primary_key=False),
		   sqlalchemy.Column('priority', sqlalchemy.Integer,
		                     nullable=False),
	           self.prepare_column(property.name, property.required_class[0], property.mandatory)]
        table = sqlalchemy.Table(table_name, self.metadata, *columns)
	return table

    def prepare_column(self, property_name, property_class, mandatory):
	"""Create a column to store the given property."""
	name = self.encode_property_name(property_name)
	type = self.get_column_type(property_class)
	nullable = not mandatory
	column = sqlalchemy.Column(name, type, nullable=nullable)
	return column

    def prepare_foreign_key_column(self, table_name, column_name, primary_key=True):
	"""Create a column referencing the given table and column."""
	foreign_key_name = '{0}.{1}'.format(table_name, column_name)
	column = sqlalchemy.Column(column_name, sqlalchemy.Integer,
		                   sqlalchemy.ForeignKey(foreign_key_name),
				   primary_key=primary_key)
	return column

    def get_column_type(self, class_):
	"""Return the sqlalchemy column type used to store the given class."""
	try:
	    return self.column_types[class_]
	except KeyError:
	    return sqlalchemy.types.NullType

    def get_property_values(self, system):
	"""Return the property values for the given system."""
	values = dict((self.encode_property_name(k), v) for k, v in system.properties.items())
	return values

    def encode_property_name(self, name):
	"""Return the database column name for a property."""
	return 'p_{0}'.format(self.sanitize_name(name))

    def decode_property_name(self, name):
	"""Return the property name associated with a database column name."""
	return self.unsanitize_name(name)[2:]

    def sanitize_name(self, name):
	"""Make a name database safe."""
	return name.replace('-', '_')

    def unsanitize_name(self, name):
	"""Reverse the effects of a sanitize_name."""
	return name.replace('_', '-')

