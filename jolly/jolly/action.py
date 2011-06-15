"""Changes in the state of the game are represented as Actions."""

class Action(object):
    """The result of a change in the state of the game."""

    def __init__(self, action_type, time, target, description, details=None, 
	         owner=None, private=False):
	"""Initialize an Action object.

           action_type: a string identifier of the type of action
	   time: the Moment the action occurred
	   target: the System targetted by the action
	   description: a human-readable description of the action
	   details: an arbitrary object with details of the action results.
	            This is dependent on the action type.
	   owner: an object in an ownership chain
	   private: True if this action is only visible to its owner
	"""
	self.action_type = action_type
	self.time = time
	self.target = target
	self.description = description
	self.details = details
	self.owner = owner
	self.private = private

