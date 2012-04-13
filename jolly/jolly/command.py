"""Commands are the primary means of interacting with the game.
   They are instantiated from a template with arguments and then placed
   in the game queue which executes them at the appropriate time."""

from functools import reduce
from heapq import heappush, heappop, heapify
import inspect
from operator import add

from jolly.action import Action

class CommandException(Exception):
    """Superclass of all command exceptions."""
class ArgumentException(CommandException):
    """Superclass of argument exceptions."""
class MissingArgument(ArgumentException):
    """A mandatory or upfront argument is not present where required."""
class InvalidArgumentType(ArgumentException):
    """The argument value is not the correct type."""
class InvalidArgument(ArgumentException):
    """The argument does not have a valid value (but is the right type)."""
class UnchangeableArgument(ArgumentException):
    """The argument value cannot be changed."""
class InvalidTime(ArgumentException):
    """The command cannot be scheduled at this time."""
class PreviouslyQueued(CommandException):
    """The command has already be queued."""
class PreviouslyExecuted(CommandException):
    """The command has already be executed."""
class PreviouslyCancelled(CommandException):
    """The command has been cancelled."""
class NotQueued(CommandException):
    """The command has not been queued."""
class CannotCancel(CommandException):
    """The command cannot be cancelled."""
class MultipleArgumentProblems(ArgumentException):
    """There are problems with multiple arguments."""
    def __init__(self, problems):
        self.problems = problems
    def __str__(self):
	return ','.join(str(p) for p in self.problems.values())

class FormalArgument(object):
    """The specification of an argument to a command."""

    def __init__(self, name, klass, mandatory=True,
                 upfront=False, can_change=False, default=None,
                 validator=None):
        self.name = name
        self.klass = klass
        self.mandatory = mandatory or upfront
        self.upfront = upfront
        self.can_change = can_change
        self.default = default
        self.validator = validator or (lambda arg: True)

    def _is_proper_class(self, value):
        """Determine whether the value has the proper class."""
        if inspect.isclass(self.klass):
            return isinstance(value, self.klass)
        for klass in self.klass:
            if isinstance(value, klass): 
                return True
        return False

    def validate_for_queue(self, value):
        """Confirm that the argument is valid for queuing."""
        if value is None:
            if self.upfront:
                raise MissingArgument(self.name)
        elif not self._is_proper_class(value):
            raise InvalidArgumentType(self.name)
        self.validator(value)

    def validate_for_change(self, old_value, new_value):
        """Confirm that the argument can be validly changed."""
        if old_value == new_value: 
            return
        if new_value is None:
            if self.upfront:
                raise MissingArgument(self.name)
        elif not self.can_change:
            raise UnchangeableArgument(self.name)            
        elif not self._is_proper_class(new_value):
            raise InvalidArgumentType(self.name)
        self.validator(new_value)

    def validate_for_execute(self, value):
        """Confirm that the argument is valid for executing."""
        if value is None:
            if self.mandatory:
                raise MissingArgument(self.name)
        elif not self._is_proper_class(value):
            raise InvalidArgumentType(self.name)
        self.validator(value)

class CommandTemplate(object):
    """Rules for queuing and executing a command."""

    def __init__(self, name, step, arguments, can_cancel=False, required=False):
        """name: the name of the template
           step: the name of the step where this command executes
           arguments: the FormalArguments for the command
           can_cancel: can the Player cancel the command
           required: must the Player perform the command each iteration"""
        
        self.name = name
        self.step = step
        self.arguments = arguments
        self.can_cancel = can_cancel
        self.required = required

    def order(self, command):
        """Provide an ordinal number for this command.
           This can be a float to interpolate between integers.
           CommandTemplate subclasses can override this to get more
           precise ordering within their time step."""
        return 0

    def validate_arguments_for_queue(self, values):
        """Determine whether the command has valid arguments for queuing."""
        problems = {}
        for arg in self.arguments:
            try:
                arg.validate_for_queue(values.get(arg.name, arg.default))
            except ArgumentException as exc:
                problems[arg.name] = exc
        if problems:
            raise MultipleArgumentProblems(problems)

    def validate_arguments_for_change(self, old_values, new_values):
        """Determine whether the command arguments are valid to change."""
        problems = {}
	clean_arguments = {}
        for arg in self.arguments:
            try:
                old_value = old_values.get(arg.name, arg.default)
                new_value = new_values.get(arg.name, old_value)
                arg.validate_for_change(old_value, new_value)
            except ArgumentException as exc:
                problems[arg.name] = exc
	    clean_arguments[arg.name] = new_value
        if problems:
            raise MultipleArgumentProblems(problems)
	return clean_arguments

    def validate_arguments_for_execute(self, values):
        """Determinine whether the command has valid arguments for execution."""
        problems = {}
        for arg in self.arguments:
            try:
                arg.validate_for_execute(values.get(arg.name, arg.default))
            except ArgumentException as exc:
                problems[arg.name] = exc
        if problems:
            raise MultipleArgumentProblems(problems)

    def validate_time(self, time):
        """Determine whether the command has a valid time."""
        if not time.name == self.step:
            raise InvalidTime(time)

    def validate_for_queue(self, command, queue, env=None):
        """Determine whether the command can be queued."""
        self.validate_arguments_for_queue(command.arguments)
        self.validate_time(command.time)
        if command.queued:
            raise PreviouslyQueued(command)

    def validate_for_change(self, command, arguments, env=None):
        """Determine whether the command arguments can be changed."""
        clean_arguments = self.validate_arguments_for_change(command.arguments, arguments)
        self.validate_time(command.time)
        if command.done:
            raise PreviouslyExecuted(command)
        if command.cancelled:
            raise PreviouslyCancelled(command)
	return clean_arguments
          
    def validate_for_execute(self, command, env=None):
        """Determine whether the command can be executed."""
        self.validate_arguments_for_execute(command.arguments)
        self.validate_time(command.time)
        if not command.queued:
            raise NotQueued(command)
        if command.done:
            raise PreviouslyExecuted(command)
        if command.cancelled:
            raise PreviouslyCancelled(command)

    def validate_for_cancel(self, command, env=None):
        """Determine whether the command can be cancelled."""
        if not self.can_cancel:
            raise CannotCancel(command)
        if command.done:
            raise PreviouslyExecuted(command)
        if command.cancelled:
            raise PreviouslyCancelled(command)

    def execute(self, command, env=None):
        """Perform the work of the command.  Override in subclasses.
	   Must return a sequence of Actions."""
        return []


class Command(object):
    """A specification of the details of an action."""

    private = True

    def __init__(self, owner, template, time, arguments):
        self.owner = owner
        self.template = template
        self.time = time
        self.arguments = arguments
        self.queue = None
        self.done = False
        self.cancelled = False

    @property
    def queued(self):
        """Return whether or not the Command is queued."""
        return not self.queue is None

    @property
    def status(self):
	if self.cancelled:
	    return 'cancelled'
	if self.done:
	    return 'done'
	if self.queued:
	    return 'queued'
	return 'unqueued'

    def insert_into_queue(self, queue, env=None):
        """Insert the Command into the given queue."""
        self.template.validate_for_queue(self, queue, env)
        queue(self)
        self.queue = queue

    def execute(self, env=None):
        """Execute the Command."""
        self.template.validate_for_execute(self, env)
        results = self.template.execute(self, env)
        self.done = True
	self.queue.unqueue(self)
	self.queue = None
	return results

    def update_arguments(self, arguments, env=None):
        """Update the arguments provided to the Command."""
        clean_arguments = self.template.validate_for_change(self, arguments, env)
        self.arguments = clean_arguments

    def cancel(self, env=None):
        """Cancel the Command."""
        self.template.validate_for_cancel(self, env)
        self.cancelled = True
	self.queue.unqueue(self)
	self.queue = None

    def create_action(self, action_type, target, description, details=None, private=False):
	action = Action(action_type, self.time, target, description, details, self.owner, private)
	return action

    def __cmp__(self, other):
	try:
            if self.time == other.time:
                diff = other.template.order(other) - self.template.order(self)
                return -1 if diff < 0 else 1 if diff > 0 else 0
            return -1 if self.time < other.time else 1
	except (AttributeError, TypeError):
	    return NotImplemented

class CommandQueue(object):
    """A priority queue of command objects."""

    private = True

    def __init__(self, commands=None, owner=None):
        self.commands = commands or []
        for c in self.commands:
            c.queue = self
	self.owner = owner

    def __call__(self, command):
        heappush(self.commands, command)

    def is_duplicate(self, command, check_arguments=None):
        """Determine whether command is already in the queue."""
        check_arguments = check_arguments or []
        return any(all(c.arguments[arg] == command.arguments[arg] for arg in check_arguments) for c in self.commands)
        
    def pop(self):
        """Return and remove the next queued Command."""
        return heappop(self.commands)

    def unqueue(self, command):
	"""Remove a specified command from the queue."""
	self.remove(lambda c: c == command)

    def remove(self, predicate):
        """Remove all queued Commands for which predicate is true."""
	self.commands = self.find(lambda c: not predicate(c))
	heapify(self.commands)

    def find(self, predicate):
        """Return all queued Commands for which predicate is true."""
        return [c for c in self.commands if predicate(c)]

    def peek(self):
        """Return the next queued Command."""
        return self.commands[0] if self.commands else None

    def __iter__(self):
        return iter(sorted(self.commands))

    def __contains__(self, command):
        return command in self.commands

class MergedCommandQueue(CommandQueue):
    """A command queue composed of commands from other CommandQueues.
       Commands are not owned by this queue."""

    def __init__(self, queues=[]):
	commands = reduce(add, [q.commands for q in queues])
	heapify(commands)
	self.commands = commands
	self.owner = None
