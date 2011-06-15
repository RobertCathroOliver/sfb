"""SFB specific map functionality."""

from jolly.map import HexLocation as Location
from jolly.map import Map, Compass, Direction, LineOfSight, Hexagon

compass = Compass([Direction('A', Location((0, -1))),
                   Direction('B', Location((1, 0))),
                   Direction('C', Location((1, 1))),
                   Direction('D', Location((0, 1))),
                   Direction('E', Location((-1, 1))),
                   Direction('F', Location((-1, 0)))],
                  Direction('0', Location((0,0))))
hexagon = Hexagon()

def get_relative_location(from_position, to_location):
    rotation = Rotation(compass, from_position.facing, compass.get('A'))
    return rotation.apply(to_location)

def has_line_of_sight(self, l1, l2):
    los = LineOfSight(compass, hexagon, l1, l2)
    for l in los:
        """ check whether there is some blocking terrain """
    return True

Map.has_line_of_sight = has_line_of_sight
        
