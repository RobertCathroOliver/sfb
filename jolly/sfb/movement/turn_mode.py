"""Turn mode definitions."""
from jolly.util import Range, RangeDict
from sfb.chrono import IMPULSES_PER_TURN

class TurnMode(object):
    """Determine whether a unit can turn."""
    
    def __init__(self, name, speeds):
        """Note: speeds is a RangeDict with speed ranges for keys and 
                 required number of forward movements as values."""
        self.name = name
        self.speeds = speeds
    
    def is_fulfilled(self, move_count, speed):
        return move_count >= self.speeds[speed]

seeking_weapon = TurnMode('seeking-weapon', 
                          RangeDict({Range(1, IMPULSES_PER_TURN) : 1}))
shuttle = TurnMode('shuttle',
                   RangeDict({Range(1, 11) : 1,
                              Range(12, 23) : 2,
                              Range(24, IMPULSES_PER_TURN) : 3}))
AA = TurnMode('AA',
              RangeDict({Range(1) : 0,
                         Range(2, 8) : 1,
                         Range(9, 16) : 2,
                         Range(17, 24) : 3,
                         Range(24, IMPULSES_PER_TURN) : 4}))
A = TurnMode('A',
             RangeDict({Range(1) : 0,
                        Range(2, 6) : 1,
                        Range(7, 12) : 2,
                        Range(13, 19) : 3,
                        Range(20, 26) : 4,
                        Range(27, IMPULSES_PER_TURN) : 5}))
B = TurnMode('B',
             RangeDict({Range(1) : 0,
                        Range(2, 5) : 1,
                        Range(6, 10) : 2,
                        Range(11, 15) : 3,
                        Range(16, 21) : 4,
                        Range(22, 28) : 5,
                        Range(29, IMPULSES_PER_TURN) : 6}))
C = TurnMode('C',
             RangeDict({Range(1) : 0,
                        Range(2, 4) : 1,
                        Range(5, 9) : 2,
                        Range(10, 14) : 3,
                        Range(15, 20) : 4,
                        Range(21, 27) : 5,
                        Range(28, IMPULSES_PER_TURN) : 6}))
D = TurnMode('D',
             RangeDict({Range(1) : 0,
                        Range(2, 4) : 1,
                        Range(5, 8) : 2,
                        Range(9, 12) : 3,
                        Range(13, 17) : 4,
                        Range(18, 24) : 5,
                        Range(25, IMPULSES_PER_TURN) : 6}))
E = TurnMode('E',
             RangeDict({Range(1) : 0,
                        Range(2, 3) : 1,
                        Range(4, 6) : 2,
                        Range(7, 10) : 3,
                        Range(11, 14) : 4,
                        Range(15, 20) : 5,
                        Range(21, 29) : 6,
                        Range(30, IMPULSES_PER_TURN) : 7}))
F = TurnMode('F',
             RangeDict({Range(1) : 0,
                        Range(2, 3) : 1,
                        Range(4, 5) : 2,
                        Range(6, 9) : 3,
                        Range(10, 13) : 4,
                        Range(14, 17) : 5,
                        Range(18, 23) : 6,
                        Range(24, 29) : 7,
                        Range(30, IMPULSES_PER_TURN) : 8}))

def setup_registry(registry):
    registry.set(seeking_weapon.name, seeking_weapon, TurnMode)
    registry.set(shuttle.name, shuttle, TurnMode)
    registry.set(AA.name, AA, TurnMode)
    registry.set(A.name, A, TurnMode)
    registry.set(B.name, B, TurnMode)
    registry.set(C.name, C, TurnMode)
    registry.set(D.name, D, TurnMode)
    registry.set(E.name, E, TurnMode)
    registry.set(F.name, F, TurnMode)
