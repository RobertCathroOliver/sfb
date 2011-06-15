# Test Location

Let l be a Location object w/ coordinates (x, y)
Then:
    l == Location(x, y)
    repr(l) == Location(x, y)
    str(l) == 'xxyy'
    abs(l) == [precalculate the distance of l from the origin]
    l - l == Location(0, 0)
    abs(l + l) == abs(l) + abs(l)


Location.create('xxyy') => Location(xx, yy)
str(Location(xx, yy)) == 'xxyy'


template = UnitTemplate(filename)
team1 = Team(name, description)
team2 = Team(name, description)
player1 = Player(name, team1)
player2 = Player(name, team2)
unit1 = Unit(name, template)
unit2 = Unit(name, template)
player1.add_unit(unit1)
player2.add_unit(unit2)
game = Game(name, description)
game.add_player(player1)
game.add_player(player2)
game.go()


GET request:
try:
    object = db.get(url)
except ObjectNotFound:
    return HttpNotFound(url)
if not user.can_view(object):
    return HttpUnauthorized(url)
try:
    canonical_object = canonize.canonize(object)
except NoCanonicalRepresentation:
    return HttpNotFound(url)
result = add_headers(canonical_object)
return HttpOK(url, encode(result))

DELETE request:
try:
    object = db.get(url)
except ObjectNotFound:
    if method_allowed(url, 'DELETE'):        
        return HttpOK(url)
    else:
        return HttpMethodNotAllowed(url)
if not user.can_delete(object):
    return HttpNotAuthorized(url)
try:
    object.delete()
except CanNotDelete:
    return HttpMethodNotAllowed(url, 'DELETE')
db.delete(url)
return HttpOK(url)

POST request:
try:
    builder = get_object_builder(url, environment)
except NoBuilderExists:
    return HttpNotImplemented(url)
try:
    object = builder.build(POST)
except InvalidParameter as err:
    return HttpBadRequest(url, err.message)
try:
    builder.activate(user, object)
except NotAllowed:
    return HttpUnauthorized(url)
db.insert(url)
try:
    canonical_object = canonize.canonize(object)
except NoCanonicalRepresentation:
    return HttpOK(url)
result = add_headers(canonical_object)
return HttpOK(url, encode(result))

PUT request:
try:
    object = db.get(url)
except ObjectNotFound:
    try:
        builder = get_object_builder(url, environment)
    except NoBuilderExists:
        return HttpNotImplemented(url)
    try:
        object = builder.build(POST)
    except InvalidParameter as err:
        return HttpBadRequest(url, err.message)
    try:
        builder.activate(user, object)
    except NotAllowed:
        return HttpUnauthorized(url)
    db.insert(url)
    return HttpOK(url)

if not user.can_view(object) or not user.can_update(object):
    return HttpUnauthorized(url)
try:
    object.update(PUT)
except NotAllowed:
    return HttpUnauthorized(url)
db.update(object)
return HttpOK(url)

"""
Object              GET     POST    PUT     DELETE
Games               public  public  x       x
Game                public  x       x       creator
Players             public  x       x       x
Player              public  x       x       x
Users               public  public  x       x
User                public  x       self    self
Units               public  x       x       x
Unit                public  x       x       x
Map                 public  x       x       x
Systems             public  x       x       x
System              public  x       x       x
Messages            public  x       x       x
Message             public  x       x       x
Command             player  x       player  player
CommandQueue        player  player  x       x       * HistoryQueue + pending commands
HistoryQueue        public  x       x       x       * Merge of players command queues for commands in the past
EnergyAllocation    unit    x       unit    x       * auto-create energy allocation on GET/PUT
SpeedPlot           unit    x       unit    x       * auto-create speed plot on GET/PUT
"""
