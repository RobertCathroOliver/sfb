import sqlalchemy
import sfb.persist
import persist_schemas
import sfb.system.hull
import sfb.system.phaser
import sfb.firing_arc
import sfb.chrono

engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
metadata = sqlalchemy.MetaData()
conn = engine.connect()

persistor = sfb.persist.System(metadata, sfb.persist.column_types)
persistor.get_table(sfb.system.hull.forward_hull)
persistor.get_table(sfb.system.phaser.phaser1)
persistor.system_table
metadata.create_all(engine)

fh = sfb.system.hull.forward_hull.create_system()
p1 = sfb.system.phaser.phaser1.create_system(
	{'firing-arc': sfb.firing_arc.FA,
	 'previous_uses' : [sfb.chrono.get_moment(1, 1, 'move'),
	                    sfb.chrono.get_moment(1, 9, 'move')]})

fh_id = persistor.save(conn, fh)
p1_id = persistor.save(conn, p1)

fh_new = persistor.load(conn, fh_id)
p1_new = persistor.load(conn, p1_id)


