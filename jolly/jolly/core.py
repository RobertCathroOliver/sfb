"""Core game objects."""
import operator, functools

from jolly.action import Action
from jolly.breakpoint import BreakPoint
from jolly.command import (CommandQueue, NotQueued, PreviouslyExecuted, 
                           PreviouslyCancelled, InvalidTime,
                           MultipleArgumentProblems, MergedCommandQueue)

class Player(object):
    """A Player in the Game."""

    def __init__(self, name, units=None, breakpoints=None, status=None, queue=None, owner=None):
        self.name = name
        self.units = units or []
        self.breakpoints = breakpoints or [BreakPoint(self, 'start-game')]
        for b in self.breakpoints:
            b.owner = self
        self.status = status or Status(self)
        self.status.owner = self
        self.queue = queue or CommandQueue()
        self.queue.owner = self
        self.owner = owner
        self.game = None
        for u in self.units:
            u.owner = self

    def check_breakpoints(self, action):
        return [b for b in self.breakpoints if b.is_triggered(action)]

    @property
    def log(self):
        if not self.game:
            return None
        return ActionLog(self, self.game.log.actions)

class User(object):
    """The representation of a person using the system."""

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def authenticate(self, password):
        """Determine whether the password is correct."""
        return self.password == password

    def is_owner(self, obj):
	while obj != None:
	    if obj == self:
	        return True
	    obj = getattr(obj, 'owner', None)
	return False

    def __eq__(self, other):
        try:
            return self.name == other.name and self.email == other.email and self.password == other.password
        except AttributeError:
            return False
        return False

class Game(object):
    """The main object representing the state of the game."""

    def __init__(self, title, sequence_of_play, map_, players, choice, log=None, queue=None):
        self.title = title
        self.sequence_of_play = sequence_of_play
        self.map = map_
        self.map.game = self
        self.players = players
        for p in self.players:
            p.game = self
        self.log = log or ActionLog(self)
        self.game_queue = queue or CommandQueue()
        self.game_queue.owner = self
        self.choice = choice
        self.last_command = None
        for action_moment in self.sequence_of_play:
            break
        self.current_time = action_moment
        action = Action('start-game', action_moment, self, 'Start Game')
        self.last_actions = [action]
        self.log_actions(self.last_actions)

    @property
    def units(self):
        """Return all the Units in the Game."""
        return functools.reduce(operator.add, [p.units for p in self.players])

    @property
    def breakpoints(self):
        """Return all the active breakpoints in the game."""
        return functools.reduce(operator.add, [p.breakpoints for p in self.players])

    @property
    def queue(self):
        """Return a queue of all the active commands in the game."""
        return MergedCommandQueue([self.game_queue] + [p.queue for p in self.players])

    def check_breakpoints(self, actions):
        breakpoints_triggered = False
        for p in self.players:
            b = functools.reduce(operator.add, [p.check_breakpoints(a) for a in actions])
            if b:
                p.status.update(Status.BREAKPOINT, b)
            else:
                p.status.update(Status.WAITING)
            breakpoints_triggered = breakpoints_triggered or not not b
        return breakpoints_triggered

    def advance(self):
        """Advance the state of the game as far as possible."""
        while True:
            try:
                # refresh the queue
                queue = self.queue

                # are there any breakpoints impeding progress?
                if self.check_breakpoints(self.last_actions):
                    print 'Initial Breakpoint at {0}'.format(self.current_time)
                    return

                # determine the next command
                next_command = queue.peek()
                
                # advance, a moment at a time, until the next command
                # checking for breakpoints
                if self.current_time != next_command.time:
                    for time in self.sequence_of_play(self.current_time):
                        self.current_time = time
                        msg = 'Advance sequence of play to {0}'.format(time)
                        action = Action('advance', time, self, msg)
                        self.last_actions = [action]
                        self.log_actions(self.last_actions)
                        if self.check_breakpoints(self.last_actions):
                            print 'Breakpoint at {0}'.format(time)
                            return
                        if time == next_command.time:
                            break
    
                # execute the next command
                print 'Command execution at {0}'.format(next_command.time)
                self.last_actions = next_command.execute(self)
                self.log_actions(self.last_actions)
               
            except (NotQueued, PreviouslyExecuted, PreviouslyCancelled, InvalidTime) as exc:
                # something bad has happened.  Log it, remove the command and
                # continue
                queue.unqueue(next_command)
            except MultipleArgumentProblems as exc:
                details = {'command': next_command}
                for k, v in exc.problems.items():
                    details[k] = str(v.__class__.__name__)
                            
                next_command.owner.status.update(Status.INPUT_REQUIRED, [details])
                print 'Input Required at {0}'.format(next_command.time)
                return

    def log_actions(self, actions):
        for a in actions:
            self.log.add(a)


class ActionLog(object):
    """A list of actions that are visible by a given owner."""

    def __init__(self, owner=None, actions=None):
        self.owner = owner
        self.actions = []
        if not actions is None:
            for a in actions:
                self.add(a)

    def add(self, action):
        if not getattr(action, 'private', False) or not self.owner or self.owner and self.owner == action.owner:
            self.actions.append(action)


class Status(object):
    """Current status for a player."""

    BREAKPOINT = 'breakpoint'
    WAITING = 'waiting'
    INPUT_REQUIRED = 'input-required'

    def __init__(self, owner, status=None, details=None):
        self.owner = owner
        self.status = status or self.WAITING
        self.details = details

    def update(self, status, details=None):
        self.status = status
        self.details = details
