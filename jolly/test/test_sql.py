import sqlalchemy as sa
import sqlalchemy.orm as orm
import jolly.sql as sql
import jolly.core as core

engine = sa.create_engine('sqlite:///:memory:', echo=True)
Session = orm.sessionmaker(bind=engine)
session = Session()

sql.metadata.create_all(engine)

