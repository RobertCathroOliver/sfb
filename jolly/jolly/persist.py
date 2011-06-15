
class Persist(object):

    def __init__(self, metadata, column_types):
	self.metadata = metadata
	self.column_types = column_types

    def save(self, connection, system):
        prototype = system.prototype
	mapper_class = self.prepare_mapper_class(prototype.name)
        mapper_table = self.get_table(prototype)
	mapper(mapper_class, mapper_table)

    def prepare_mapper_class(self, prototype):
	class_name = '{0}Mapper'.format(self.sanitize(prototype.name))
	formal_properties = [p for s in prototype.services for p in s.properties]
	def to_system(this):
	    properties = {}
	    for p in formal_properties:
		key = self.encode_property_name(p.name)
                properties[p.name] = getattr(this, key, None)
	    system = prototype.create_system(properties)
	    return system
	class_dict = {to_system.__name__: to_system}

	class_ = type(class_name, (object,), class_dict)
	return class_

    def prepare_mapper_table(self, prototype):
	table_name = '{0}_system'.format(self.sanitize(prototype.name))
	columns = [self.prepare_foreign_key_column('systems', 'system_id')]
	formal_properties = [p for s in prototype.services for p in s.properties]
	for p in formal_properties:
	    column_name = self.encode_property_name(p.name)
	    column = self.prepare_column(column_name, p.required_class, p.mandatory)
	    columns.append(column)
	table = sqlalchemy.Table(table_name, self.metadata, *columns)
	return table

    def prepare_column(self, name, type_, mandatory):
	"""Create a column definition."""
	column_name = self.sanitize(name)
	column_type = self.get_column_type(type_)
        nullable = not mandatory
	column = sqlachemy.Column(column_name, column_type, nullable=nullable)
	return column


	




