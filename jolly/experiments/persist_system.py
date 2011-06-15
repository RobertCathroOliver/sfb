"""
Tables:
    systems
    	system_id
	prototype

    hull_systems
        system_id
        damage_arc
	damage_status

load(system_id):
    prototype_name = select prototype from systems where system_id=<system_id>
    prototype = retrieve(prototype_name)
    table_name = get_table_name(prototype.name)
    propert
      
"""

class SchemaBuilder(object):

    def __init__(self, metadata, column_types):
	self.metadata = metadata
	self.column_types = column_types

    def define_table(self, table_name, columns):
	table = sqlalchemy.Table(table_name, self.metadata, *columns)
	return table

    def define_column(self, column_name, class_, mandatory=True):
	column_type = self.get_db_column_type(class_)
	nullable = not mandatory
	column = sqlalchemy.Column(column_name, column_type, nullable=nullable)
	return column

    def define_foreign_key_column(self, table):
	primary_key = table.primary_key
	column = self.define_column(primary_key.name, int, True)



    def define_list(self, base_table, list_name, class_, mandatory=True):
	table_name = '{0}_list'.format(list_name)
	columns = [sqlalchemy.Column('id', sqlalchemy.Integer,
	                             primary_key=True),
		   self.define_foreign_key_column(base_table),
                   sqlalchemy.Column('priority', sqlalchemy.Integer,
		                     nullable=False),
		   self.define_column(list_name, class_, mandatory)]
	table = self.define_table(table_name, columns)
	return table






    def get_db_column_type(self, class_):
	try:
	    return self.column_types[class_]
	except KeyError:
	    return sqlalchemy.types.NullType
"""

"""
