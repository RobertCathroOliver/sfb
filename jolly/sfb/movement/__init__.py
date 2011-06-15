# These imports are only meant to be used in this file
from jolly.util import RangeDict, Range
from sfb.chrono import IMPULSES_PER_TURN, get_moment

# These imports are part of the public API
from sfb.movement.turn_mode import TurnMode

__all__ = ['SpeedPlot', 'AccelerationLimit', 'make_speed_plot', 'TurnMode']

class SpeedPlot(object):
    """Represent the speed of a unit and the impulses on which it moves."""

    def __init__(self, speeds):
        """speeds is a RangeDict with {impulse-range : integer speed }"""
        self.speeds = speeds

    def has_move(self, impulse):
	import math
        speed = self.speeds[impulse]
        return impulse in [int(math.ceil(float(IMPULSES_PER_TURN) / speed * (i + 1))) - 1 for i in range(speed)]
 
    def get_speed(self, impulse):
        return self.speeds[impulse]

    def get_minimum_speed(self, start_impulse, end_impulse):
        if start_impulse > end_impulse: return None
        min_speed = None
        for r, speed in self.speeds.items():
            if start_impulse in r or end_impulse in r or (start_impulse < r.begin and end_impulse > r.end):
                if min_speed is None or speed < min_speed: min_speed = speed
        return min_speed

    def is_valid(self, acceleration_limit, prev_speed_plot):
        for i in range(IMPULSES_PER_TURN):
            if self.get_speed(i) > acceleration_limit.get_maximum_speed(i, self, prev_speed_plot): return False
        return True

    def get_altered_speed_plot(self, new_speed, change_impulse):
        speeds = {}
        for r, speed in self.speeds.items():
            if change_impulse > r.end:
                speeds[r] = speed
            elif change_impulse in r:
                speeds[Range((r.begin, change_impulse - 1))] = speed
                speeds[Range((change_impulse, IMPULSES_PER_TURN - 1))] = new_speed
        return SpeedPlot(RangeDict(speeds))

    def unqueue_move_commands(self, queue):
        queue.remove(lambda c: c.issuer == self)

    def create_move_commands(self, unit, turn, from_impulse=0):
        commands = []
        for i in range(from_impulse, IMPULSES_PER_TURN):
            if self.has_move(i):
                moment = get_moment(turn, i, 'move')
                commands.append(Command(self, move, moment, {'unit' : unit}))
        return commands

    def __iter__(self):
	for i in range(IMPULSES_PER_TURN):
	    if self.has_move(i):
		yield i

    def queue_move_commands(self, queue, commands):
        for cmd in commands:
            cmd.insert_into_queue(queue)

    def setup_move_commands(self, queue, unit, turn, from_impulse=0):
        self.unqueue_move_commands(queue)
        commands = self.create_move_commands(unit, turn, from_impulse)
        self.queue_move_commands(queue)

    def get_update_observer(self, queue, unit, turn, from_impulse=0):
        def manage_move_commands(system, state, old_value, new_value):
            old_value.cancel_move_commands(queue)
            commands = new_value.create_move_commands(unit, turn, from_impulse)
            new_value.queue_move_commands(queue, commands)
        return manage_move_commands

class AccelerationLimit(object):
    """Represents the limits to acceleration of a Unit."""

    def __init__(self, max_speed, max_addition, max_multiple):
        self.max_speed = max_speed
        self.max_addition = max_addition
        self.max_multiple = max_multiple

    def get_maximum_speed(self, impulse, speed_plot, prev_speed_plot=None):
        low = speed_plot.get_minimum_speed(0, impulse - 1)
        if not prev_speed_plot is None:
            low = min(low, prev_speed_plot.get_minimum_speed(impulse, IMPULSES_PER_TURN - 1))
        if low is None: low = self.max_speed
        maximum_speed = min(self.max_speed, max(low + self.max_addition, low * self.max_multiple))
        return maximum_speed
            
def make_speed_plot(speed):
    return SpeedPlot(RangeDict({Range(0, IMPULSES_PER_TURN - 1) : speed}))
