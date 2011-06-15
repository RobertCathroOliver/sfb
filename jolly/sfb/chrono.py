"""Customize jolly.chrono for SFB."""

from jolly.chrono import load_sequence_of_play, Moment
import settings

SOP = load_sequence_of_play(settings.SEQUENCE_OF_PLAY)
IMPULSES_PER_TURN = int(SOP.root[6].attrib['repeat'])

Moment.turn = property(lambda self: self.multiple[0])
Moment.impulse = property(lambda self: self.path[0] == 6 and (self.multiple[1]) or None)
Moment.step = property(lambda self: self.name)
Moment.__unicode__ = lambda self: '{0}.{1}.{2}'.format(self.turn + 1, self.impulse + 1, self.step) if self.impulse else '{0}.{1}'.format(self.turn + 1, self.step)
Moment.__str__ = Moment.__unicode__

def get_moment(turn, impulse, step):
    moment = SOP.get_moment(step)
    moment.multiple[0] = turn
    if impulse:
        if moment.path[0] == 6:
            moment.multiple[1] = impulse
        else:
            raise ValueError
    elif moment.path[0] == 6:
        raise ValueError()
    return moment

class Duration(object):

    def __init__(self, turns, impulses=None):
        self.turns_only = impulses is None
        self.impulses = turns * IMPULSES_PER_TURN + (impulses or 0)

    def __add__(self, other):
        if not isinstance(other, Duration): return NotImplemented
        if self.turns_only != other.turns_only:
            raise TypeError
        result = Duration(0, self.impulses + other.impulses)
        result.turns_only = self.turns_only
        return result

    def __radd__(self, other):
        if not isinstance(other, Moment): return NotImplemented
        if other.impulse is None and not self.turns_only:
            raise TypeError
        result = SOP.get_moment(other.name)
        if other.impulse:
            impulses = self.impulses % IMPULSES_PER_TURN + other.impulse - 1
            result.multiple[0] = self.impulses // IMPULSES_PER_TURN + impulses // IMPULSES_PER_TURN + other.turn - 1
            result.multiple[1] = impulses % IMPULSES_PER_TURN
        else:
            result.multiple[0] = self.impulses // IMPULSES_PER_TURN + other.turn - 1
        return result
        
