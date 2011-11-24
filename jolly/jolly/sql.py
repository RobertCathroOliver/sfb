"""
SQL Alchemy mapping.
"""

import numbers
from sqlalchemy import Table, MetaData, Column, ForeignKey, Boolean, Integer, String
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from jolly.core import User
from jolly.map import Map, MapBound

metadata = MetaData()

game_table = Table('games', metadata,
           Column('game_id', Integer, primary_key=True),
           Column('title', String(100)))

player_status_table = Table('player_status', metadata,
                    Column('player_status_id', Integer, primary_key=True),
                    Column('name', String(50)))

player_table = Table('players', metadata,
             Column('player_id', Integer, primary_key=True),
             Column('game_id', Integer, ForeignKey('games.game_id')),
             Column('user_id', Integer, ForeignKey('users.user_id')),
             Column('name', String(100)),
             Column('status_id', Integer, ForeignKey('player_status.player_status_id')))

user_table = Table('users', metadata,
           Column('user_id', Integer, primary_key=True),
           Column('name', String(100)),
           Column('email', String(255)),
           Column('password', String(100)))

mapper(User, user_table)

action_type_table = Table('action_types', metadata,
                   Column('action_type_id', Integer, primary_key=True),
                   Column('name', String(50)),
                   Column('detail', String(50)))

action_table = Table('actions', metadata,
              Column('action_id', Integer, primary_key=True),
              Column('owner_id', Integer, ForeignKey('players.player_id')),
              Column('action_type_id', Integer, ForeignKey('action_types.action_type_id')),
              Column('time', String(50)),
              Column('description', String),
              Column('target_id', Integer, ForeignKey('systems.system_id')),
              Column('private', Boolean))

command_table = Table('commands', metadata,
               Column('command_id', Integer, primary_key=True),
               Column('owner_id', Integer, ForeignKey('players.player_id')),
               Column('template', String(50)),
               Column('time', String(50)),
               Column('done', Boolean),
               Column('cancelled', Boolean))

command_argument_table = Table('command_arguments', metadata,
                        Column('command_argument_id', Integer, primary_key=True),
                        Column('command_id', Integer, ForeignKey('commands.command_id')),
                        Column('argument_name', String(50)),
                        Column('argument_type', String(50)),
                        Column('argument_value', String))

map_table = Table('maps', metadata,
           Column('map_id', Integer, primary_key=True))

map_bound_table = Table('map_bounds', metadata,
                 Column('map_bound_id', Integer, primary_key=True),
                 Column('map_id', Integer, ForeignKey('maps.map_id')),
                 Column('dimension', Integer),
                 Column('minimum', Integer),
                 Column('maximum', Integer))

mapper(Map, map_table, properties={
    'bounds': relationship(MapBound,
                           collection_class=ordering_list('dimension'), 
                           order_by=[map_bound_table.c.dimension])
})
mapper(MapBound, map_bound_table);

system_table = Table('systems', metadata,
              Column('system_id', Integer, primary_key=True),
              Column('id', String),
              Column('prototype', String(50)),
              Column('parent_id', Integer, ForeignKey('systems.system_id')),
              Column('owner_id', Integer, ForeignKey('players.player_id')))

system_property_table = Table('system_properties', metadata,
                        Column('system_property_id', Integer, primary_key=True),
                        Column('system_id', Integer, ForeignKey('systems.system_id')),
                        Column('property_name', String(50)),
                        Column('property_type', String(50)),
                        Column('property_value', String))
