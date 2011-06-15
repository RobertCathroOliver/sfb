from jolly.system import Service, PropertyDefinition
from sfb.chrono import Duration, Moment

class FrequencyRestriction(Service):

    def __init__(self):
        props = [PropertyDefinition('time-between-use', Duration, True,
                                  Duration(0, 8)),
                 PropertyDefinition('uses-per-turn', int, True, 1),
                 PropertyDefinition('previous-uses', [Moment], True, [])]
        super(FrequencyRestriction, self).__init__('frequency-restriction', props)

    def can_use(self, system, time):
        previous_uses = system.get_property('previous_uses')
        if len(previous_uses) == 0: return True
        interval = system.get_property('time-between-use')
        uses_per_turn = system.get_property('uses-per-turn')
        uses_this_turn = sum(1 for t in previous_uses if t.turn == time.turn)
        return previous_uses[-1] + interval < time and uses_this_turn < uses_per_turn

    def record_use(self, system, time):
        previous_uses = system.get_property('previous-uses')
        system.update('previous-uses', previous_uses + [time])
