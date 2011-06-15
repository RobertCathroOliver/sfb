"""Breakpoints prevent the sequence of play from advancing."""

class BreakPoint(object):
    """Superclass for other types of breakpoints."""

    private = True

    def __init__(self, owner, action_type):
        self.owner = owner
        self.action_type = action_type

    def is_triggered(self, action):
	"""Determine whether a given action triggers this breakpoint."""
        return action.action_type == self.action_type 


class SequenceOfPlayBreakPoint(BreakPoint):
    """Break at a given time in the sequence of play."""

    action_type = 'advance'

    def __init__(self, owner, time):
        self.owner = owner
        self.time = time

    def is_triggered(self, action):
        return action.action_type == self.action_type and action.time == self.time


class PropertyChangeBreakPoint(BreakPoint):
    """Break when a given property changes on a given system (or its subsystems."""

    action_type = 'property-change'

    def __init__(self, owner, system, property_name):
        self.owner = owner
        self.system = system
        self.property_name = property_name

    def is_triggered(self, action):
        property = self.system.get_property(self.property_name)
        return (action.action_type == self.action_type 
                and action.target == property
                or any(action.target == s.get_property(self.property_name)
                       for s in self.system.subsystems if s.has_property(self.property_name)))

