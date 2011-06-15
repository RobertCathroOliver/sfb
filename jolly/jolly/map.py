"""Provide core map functionality."""

import math
import re

class Direction(object):
    """A direction vector that can be added to Location objects to provide a
       new Location."""

    def __init__(self, name, vector):
        self.name = name
        self.vector = vector

    def __radd__(self, location):
        return location + self.vector

    def __repr__(self):
        return u"Direction('{0:s}')".format(self.name)

    def __unicode__(self):
        return self.name

    __str__ = __unicode__

class LocationsNotAdjacentError(Exception): pass

class Compass(object):
    """Manages relationships between directions."""

    def __init__(self, cardinal, identity):
        self.directions = {}
        count = len(cardinal)
	def setup_directions(d, cw, ccw, opposite, self):
	    d.cw = cw
	    d.ccw = ccw
            d.opposite = opposite
	    d.self = self
        for i, d in enumerate(cardinal):
	    setup_directions(d, cardinal[(i + 1) % count],
                                cardinal[(i - 1) % count],
                                cardinal[(i + count / 2) % count],
                                cardinal[i])
            self.directions[d.name] = d
        identity.cw = lambda: identity
        identity.ccw = lambda: identity
        identity.opposite = lambda: identity
        identity.self = lambda: identity
        self.directions[identity.name] = identity
        self.cardinal = cardinal
        self.identity = identity

    def get(self, name):
        """Provide named direction access."""
        return self.directions[name]

    def __contains__(self, name):
       return name in self.directions

    def __call__(self, index):
        """Provide indexed direction access."""
        return self.cardinal[index % len(self.cardinal)]

    def __iter__(self):
        return iter(self.cardinal)

    def index(self, name):
        """Return the index associated with a given direction name."""
        return list(self.cardinal).index(self.get(name))

    def direction(self, A, B):
        """Determine the direction from location A to B."""
        diff = A - B
        for d in self:
            if d == Direction(d.name, diff): return d
        raise LocationsNotAdjacentError, "locations are not adjacent"

    def __repr__(self):
        return u'<Compass()>'

    def __unicode__(self):
        return u', '.join(self.directions.keys())

    __str__ = __unicode__

class Rotation(object):
    """Rotates a location about the origin by compass points."""

    def __init__(self, compass, initial_dir, becomes_dir):
        self.compass = compass
        self.rindex = compass.index(becomes_dir) - compass.index(initial_dir)

    def apply(self, location):
        """Return the rotated location."""
        route = make_route(location.origin, location, list(self.compass))
        rotated = Route([self.compass(self.compass.index(d.name) + self.rindex) for d in route])
        return rotated.root(location.origin)[-1]

class BasePath(object):
    """A common ancestor for Paths and Routes."""

    def __init__(self, steps):
        self.path = steps

    def __len__(self):
        return len(self.path)

    def __getitem__(self, index):
        return self.path[index]

    def __iter__(self):
        return iter(self.path)

class Path(BasePath):
    """A sequence of adjacent locations."""

    def __contains__(self, location):
        return location in self.path

    def offset(self, location):
        """Offsets each step of self by location to create a new path."""
        return Path([location + l for l in self])

    def __repr__(self):
        return u'Path({0})'.format(self.path)

    def __unicode__(self):
        return unicode(self.path)

    __str__ = __unicode__

class Route(BasePath):
    """A sequence of directions."""

    def root(self, location):
        """Builds a Path by following self from location."""
        steps = [location]
        cur = location
        for d in self:
            cur = cur + d
            steps.append(cur)
        return Path(steps)

class NoRouteExistsError(Exception): pass

def make_route(start, end, bias):
    """Create a route from location start to location end."""
    steps = []
    cur = start
    dist = distance(cur, end)
    while dist > 0:
        for dir in bias:
            tmp = distance(cur + dir, end)
            if tmp < dist:
                cur = cur + dir
                steps.append(cur)
                dist = tmp
                break
        else:
            raise NoRouteExistsError, "no route found"
    return Route(steps)

def make_path(start, end, bias):
    """Create a path from location start to location end."""
    return make_route(start, end, bias).root(start)

class OutOfBoundsError(Exception): pass
class DuplicateItemError(Exception): pass

class Token(object):
    """An item on a map.  Used only by Map objects."""

    def __init__(self, item, position):
        self.item = item
        self.position = position


class Map(object):
    """A bounded container that associates items with positions."""
   
    def __init__(self, bounds):
        self.bounds = bounds
	self.inbounds = [lambda *c: all(0 <= a < b for a, b in zip(c, bounds))]
        self.tokens = []
        self.game = None

    def __contains__(self, location):
        """Determine whether location is within map bounds."""
        return location in LocationMask('map', self.inbounds)

    def has_item(self, item):
	"""Return if the token is on the map."""
	return item in [t.item for t in self.tokens]

    def add(self, item, position):
	"""Add the item to the map at position, if possible."""
	if not position in self:
            raise OutOfBoundsError("item is out of bounds")
	if self.has_item(item):
            raise DuplicateItemError("item is already on map")
	self.tokens.append(Token(item, position))

    def remove(self, item):
	"""Remove the item from the map."""
	for i, token in enumerate(self.tokens):
	    if token.item == item:
	        del self.tokens[i]
		break

    def __repr__(self):
        return u'Map({0})'.format(self.bounds) 


class LocationMask(object):
    """Tests whether a relationship between locations exists."""

    def __init__(self, name, tests):
        self.name = name
        self.tests = tests

    def __contains__(self, location):
        return any(t(*location.coordinates) for t in self.tests)

    def __repr__(self):
        return u"<LocationMask('{0}')>".format(self.name)

    def __unicode__(self):
        return self.name

    __str__ = __unicode__

class Position(object):
    """Location and facing on a map."""

    def __init__(self, location, facing):
        self.location = location
        self.facing = facing

    @property
    def coordinates(self):
        return self.location.coordinates

    def __eq__(self, other):
	if isinstance(other, Position):
            return self.location == other.location and self.facing == other.facing
	return NotImplemented

    def __abs__(self):
        """Return the distance from the origin."""
        return abs(self.location)

    def __add__(self, location):
        """Return the vector addition of self and location."""
	if not hasattr(location, 'coordinates'):
	    return NotImplemented
        return self.__class__(self.location + location, self.facing)

    def __sub__(self, location):
        """Return the vector subtraction of location from self."""
        return self + (-location)

    def __neg__(self):
        """Return the reflection of self through the origin."""
        return self.__class__(-self.location, self.facing)

    def __repr__(self):
        return u"Position('{0}', '{1}')".format(self.location, self.facing)

    def __unicode__(self):
        return u'{0}{1}'.format(self.location, self.facing)

    __str__ = __unicode__


class Bearing(object):
    """Bearing is to position as direction is to location.
       rotation_direction may be either 'ccw' or 'cw' or 'opposite' or 'self'
       This only works for directions that are registered in a Compass."""

    def __init__(self, offset_direction, rotation_direction):
        self.offset_direction = offset_direction
        self.rotation_direction = rotation_direction

    def is_rotation(self):
        return self.rotation_direction != 'self'

    def is_straight(self, position):
        return self.offset_direction == position.facing or\
               self.offset_direction == position.facing.opposite

    def __radd__(self, position):
        """Return the vector addition of position and self."""
	try:
	    location = position.location + self.offset_direction
	    facing = getattr(position.facing, self.rotation_direction)
	except AttributeError:
	    return NotImplemented
        return position.__class__(location, facing)


def distance(A, B):
    """Calculate the distance between two locations."""
    return abs(A - B)

class Location(object):
    """Base class for Coordinates on a map.  

       Override __add__ and __neg__ to implement."""

    def __init__(self, coordinates):
        self.coordinates = coordinates

    @property
    def origin(self):
        return self.__class__(tuple(0 for x in self.coordinates))

    def __eq__(self, other):
	if isinstance(other, Location):
            return all(x == y for (x, y) in zip(self.coordinates, other.coordinates))
	return NotImplemented

    def __ne__(self, other):
        return self.coordinates != other.coordinates

    def __hash__(self):
        return reduce(lambda x, y: x ^ y, self.coordinates)

    def __repr__(self):
        return u'Location({0})'.format(self.coordinates)

    def __abs__(self):
        return NotImplemented

    def __add__(self, other):
        return NotImplemented

    def __neg__(self):
        return NotImplemented
        
    def __sub__(self, other):
        return self + (-other)

    @classmethod
    def parse(cls, value):
	try:
            coordinates = map(int, re.findall(cls.in_format, value)[0])
            return cls(coordinates)
        except IndexError:
            raise ValueError(value)

    def __unicode__(self):
        return self.out_format.format(*self.coordinates)

    __str__ = __unicode__

class HexLocation(Location):
    """Hexagon coordinates."""

    out_format = u'{0:02d}{1:02d}'
    in_format = r'^(\d\d)(\d\d)$'

    def __abs__(self):
        x, y = self.coordinates
        if x % 2 == 1 and y < 0 and abs(y) >= (abs(x) + 1) / 2:
            yoff = 1
        else:
            yoff = 0
        return max(abs(x), abs(y) + abs(x) / 2 + yoff)
    
    def __add__(self, other):
	if not hasattr(other, 'coordinates'):
	    return NotImplemented
        (sx, sy), (ox, oy) = self.coordinates, other.coordinates
        return self.__class__((sx + ox, sy + oy - (sx * ox) % 2))

    def __neg__(self):
        x, y = self.coordinates
        return self.__class__((-x, -y + x % 2))


class GridLocation(Location):
    """Grid coordinates."""

    def __abs__(self):
        x, y = self.coordinates
        return max(abs(x), abs(y))

    def __add__(self, other):
	if not hasattr(other, 'coordinates'):
	    return NotImplemented
        (sx, sy), (ox, oy) = self.coordinates, other.coordinates
        return self.__class__((sx + ox, sy + oy))

    def __neg__(self):
        x, y = self.coordinates
        return self.__class__((-x, -y))

    def __unicode__(self):
        return unicode(self.coordinates)

    __str__ = __unicode__
        
class LineOfSight(object):
    """The Locations intersected by a straight line."""

    def __init__(self, compass, shape, line_start, line_end):
        self.compass = compass
        self.shape = shape
        self.start = line_start
        self.end = line_end

    def __len__(self):
        if not self.locations: self._build()
        return len(self.locations)

    def __iter__(self):
        if not self.locations: self._build()
        return iter(self.locations)

    def __contains__(self, location):
        if not self.locations: self._build()
        return location in self.locations

    LEFT, STRAIGHT, RIGHT = range(-1, 2)
    def _turns(self, (x0, y0), (x1, y1), (x2, y2)):
        """Determine where point p2 falls in relation to line (p0, p1)."""
        cross = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if cross > 0:
            return self.LEFT
        elif cross < 0:
            return self.RIGHT
        else:
            return self.STRAIGHT

    def _build(self):
        """Determine locations along a line between _start and _end."""
        start = self.shape.translate(self.start.coordinates)
        end = self.shape.translate(self.end.coordinates)
        result = []
        current = [self.start]
        while True:
            result.extend(current)
            if self.end in result: break
            current = self._next(current, result, start, end)
        return result

    # TODO: This likely doesn't work with Squares
    def _next(self, current, done, start, end):
        """Find next locations along line."""
        next = []
        for c in current:
            cdist = distance(c, self.end)
            h = self.shape.vertices(self.shape.translate(c.coordinates))
            for i, v in enumerate(h):
                turn1 = self._turns(start, end, v)
                turn2 = self._turns(start, end, h[(i + 1) % len(h)])
                if turn1 == self.STRAIGHT or turn2 == self.STRAIGHT or turn1 != turn2:
                    adj = c + self._compass(i)
                    adist = distance(adj, self.end)
                if not adj in done and not adj in next and adist < cdist:
                    next.append(adj)
                if turn1 == self.STRAIGHT:
                    adj = c + self.compass(i - 1)
                    adist = distance(adj, self.end)
                    if not adj in done and not adj in next and adist < cdist:
                        next.append(adj)
                if turn2 == self.STRAIGHT:
                    adj = c + self.compass(i + 1)
                    adist = distance(adj, self.end)
                    if not adj in done and not adj in next and adist < cdist:
                        next.append(adj)
        return next
                    
class Shape(object):

    def translate(self, coordinates):
        return NotImplemented

    def vertices(self, coordinates):
        return NotImplemented

class Hexagon(Shape):

    def translate(self, coordinates):
        x, y = coordinates
        return (1.5 * x, math.sqrt(3.0) * (y - (x % 2) / 2.0))

    def vertices(self, coordinates):
        x, y = coordinates
        offsets = ((-0.5, -math.sqrt(3.0) / 2.0),
                   (0.5, -math.sqrt(3.0) / 2.0),
                   (1, 0),
                   (0.5, math.sqrt(3.0) / 2.0),
                   (-0.5, math.sqrt(3.0) / 2.0),
                   (-1, 0))
        return [(x + xoff, y + yoff) for (xoff, yoff) in offsets]

class Square(Shape):

    def translate(self, coordinates):
        return coordinates

    def vertices(self, coordinates):
        x, y = coordinates
        offsets = ((-0.5, -0.5),
                   (0.5, -0.5),
                   (0.5, 0.5),
                   (-0.5, 0.5)) 
        return [(x + xoff, y + yoff) for (xoff, yoff) in offsets]

hexcompass = Compass([Direction('A', HexLocation((0, -1))),
                      Direction('B', HexLocation((1, 0))),
                      Direction('C', HexLocation((1, 1))),
                      Direction('D', HexLocation((0, 1))),
                      Direction('E', HexLocation((-1, 1))),
                      Direction('F', HexLocation((-1, 0)))],
                     Direction('0', HexLocation((0,0))))
