from jolly.system import Prototype
from sfb.system.service import DamageTarget, DirectFire, FrequencyRestriction
from sfb.damage import phaser_damage
from jolly.util import Range, RangeDict

class Phaser(Prototype):

    def __init__(self, name, damage_lookup):
        services = (DamageTarget(('phaser', 'any-weapon', 'excess-damage')),
                    DirectFire(damage_lookup, phaser_damage),
                    FrequencyRestriction())
        super(Phaser, self).__init__(name, services)

class ShuttlePhaser(Prototype):

    def __init__(self, name, damage_lookup):
        services = (DirectFire(damage_lookup, phaser_damage),
                    FrequencyRestriction())
        super(ShuttlePhaser, self).__init__(name, services)

damage_lookup = {}
damage_lookup['phaser-1'] =\
    RangeDict({Range(0) : (9, 8, 7, 6, 5, 4),
               Range(1) : (8, 7, 5, 4, 4, 4),
               Range(2) : (7, 6, 5, 4, 4, 3),
               Range(3) : (6, 5, 4, 4, 4, 3),
               Range(4) : (5, 5, 4, 4, 3, 2),
               Range(5) : (5, 4, 4, 3, 3, 2),
               Range(6, 8) : (4, 3, 3, 2, 1, 0),
               Range(9, 15) : (3, 2, 1, 0, 0, 0),
               Range(16, 25) : (2, 1, 0, 0, 0, 0),
               Range(26, 50) : (1, 1, 0, 0, 0, 0),
               Range(51, 75) : (1, 0, 0, 0, 0, 0)})

damage_lookup['phaser-2'] =\
    RangeDict({Range(0) : (6, 6, 6, 5, 5, 5),
               Range(1) : (5, 5, 4, 4, 4, 3),
               Range(2) : (5, 4, 4, 4, 3, 3),
               Range(3) : (4, 4, 4, 3, 3, 3),
               Range(4, 8) : (3, 2, 1, 1, 0, 0),
               Range(9, 15) : (2, 1, 1, 0, 0, 0),
               Range(16, 30) : (1, 1, 0, 0, 0, 0),
               Range(31, 50) : (1, 0, 0, 0, 0, 0)})

damage_lookup['phaser-3'] =\
    RangeDict({Range(0) : (4, 4, 4, 4, 4, 3),
               Range(1) : (4, 4, 4, 4, 3, 3),
               Range(2) : (4, 4, 4, 3, 2, 1),
               Range(3) : (3, 2, 1, 0, 0, 0),
               Range(4, 8) : (1, 1, 0, 0, 0, 0),
               Range(9, 15) : (1, 0, 0, 0, 0, 0)})

damage_lookup['phaser-4'] =\
    RangeDict({Range(0, 3) : (20, 20, 20, 20, 15, 15),
               Range(4, 5) : (20, 20, 15, 15, 12, 10),
               Range(6) : (20, 15, 12, 11, 10, 9),
               Range(7) : (15, 12, 11, 10, 9, 8),
               Range(8) : (12, 11, 10, 9, 8, 7),
               Range(9) : (10, 9, 8, 8, 7, 6),
               Range(10) : (8, 8, 7, 6, 5, 5),
               Range(11, 13) : (6, 6, 5, 4, 3, 3),
               Range(14, 17) : (5, 4, 4, 3, 2, 1),
               Range(18, 25) : (4, 3, 2, 1, 0, 0),
               Range(26, 40) : (3, 2, 1, 0, 0, 0),
               Range(41, 70) : (2, 1, 0, 0, 0, 0),
               Range(71, 100) : (1, 0, 0, 0, 0, 0)})

phaser1 = Phaser('phaser-1', damage_lookup['phaser-1'])
phaser2 = Phaser('phaser-2', damage_lookup['phaser-2'])
phaser3 = Phaser('phaser-3', damage_lookup['phaser-3'])
phaser4 = Phaser('phaser-4', damage_lookup['phaser-4'])
phaserG = Phaser('phaser-G', damage_lookup['phaser-3'])

shuttle_phaser1 = ShuttlePhaser('shuttle-phaser-1', damage_lookup['phaser-1'])
shuttle_phaser2 = ShuttlePhaser('shuttle-phaser-2', damage_lookup['phaser-2'])
shuttle_phaser3 = ShuttlePhaser('shuttle-phaser-3', damage_lookup['phaser-3'])
shuttle_phaserG = ShuttlePhaser('shuttle-phaser-G', damage_lookup['phaser-3'])
