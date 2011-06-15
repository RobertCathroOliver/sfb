"""Represent and manipulate the sequence of play."""

__all__ = ['load_sequence_of_play', 'SequenceOfPlay', 'Moment']

from copy import copy

class SequenceOfPlay(object):
    """Manage the order of events in the game."""

    def __init__(self, root):
	"""Initialize the SequenceOfPlay.

	root: an xml.etree.ElementTree root element
	"""
        self.root = root

    def get_moment(self, name):
        """Return the first instance of a named moment."""
        for m in self._iterate(use_repetitions=False):
            if m.name == name:
                m.multiple = [0 for x in m.multiple]
                return m
        raise KeyError(name)

    def __call__(self, start):
        """Return an iterator starting at moment start."""
        return self._iterate(start)

    def __iter__(self):
        """Return an iterator starting at the first moment."""
        return self._iterate()
    
    def _iterate(self, start=None, use_repetitions=True):
        """Iterate through the leaf elements of the sequence of play."""
        path = start and start.path or [] # path to start
        multiple = start and start.multiple or [-1] # multiple to start

        elements = [] # a stack of elements
        cur = self.root # current element
        index = 0 # the next child element to examine
    
        def get_repetitions(element):
            """Return the number of times an element is repeated."""
            return int(element.attrib.get('repeat', 1))
    
        # go to start
        for i in path:
            elements.append(cur)
            cur = cur[i]
        multiple[-1] += 1

        try:
            while True:
                repetitions = get_repetitions(cur)
                if multiple[-1] >= repetitions and repetitions != 0:
                    index = path.pop() + 1
                    multiple.pop()
                    cur = elements.pop()
                elif len(cur) == 0:
                    yield Moment(cur.get('name'), cur.get('descr'), copy(path), copy(multiple))
                    multiple[-1] += 1
                elif index < len(cur):
                    path.append(index)
                    multiple.append(0)
                    elements.append(cur)
                    cur = cur[index]
                    index = 0
                    if not use_repetitions: multiple[-1] = get_repetitions(cur) - 1
                else:
                    multiple[-1] += 1
                    index = 0
        except IndexError:
            pass # iteration is done
    
def load_sequence_of_play(filename):
    """Load a sequence of play from an XML file."""
    import xml.etree.ElementTree as ET
    return SequenceOfPlay(ET.parse(filename).getroot())

class Moment(object):
    """A discrete, distinct point in the sequence of play."""

    def __init__(self, name, descr, path, multiple):
        self.name, self.description = name, descr
        self.path, self.multiple = path, multiple

    def __eq__(self, other):
        return self.path == other.path and self.multiple == other.multiple

    def __ne__(self, other):
        return not (self == other)

    def  __hash__(self):
        return hash(tuple(self.path)) ^ hash(tuple(self.multiple))

    def __lt__(self, other):
        if self == other: return False
        if self.multiple[0] != other.multiple[0]:
            return self.multiple[0] < other.multiple[0]
        for i, (s, o) in enumerate(zip(self.path, other.path)):
            if s != o: return s < o
            if self.multiple[i + 1] != other.multiple[i + 1]:
                return self.multiple[i + 1] < other.multiple[i + 1]
        return False

    def __gt__(self, other):
        return other < self

    def __repr__(self):
        return u"Moment('{0}', '{1}', {2}, {3})".format(self.name, self.description, self.path, self.multiple)

    def __unicode__(self):
        return self.name

    __str__ = __unicode__
