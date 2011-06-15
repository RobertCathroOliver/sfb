from jolly.resource import ResourceType

damage = ResourceType('damage')
phaser_damage = ResourceType('phaser', [damage])

def is_valid_target(system_type, incident, damage_type):
    def predicate(system):
        try:
            target = system.use_as('damage-target')
            return target.is_damageable() and\
                   target.is_damageable_as(system_type) and\
                   target.is_damageable_by(damage_type) and\
                   target.is_damageable_from(incident)
        except:
            return False
    return predicate

class RuleSet(object):
    def __init__(self, system_types):
        self.system_types = system_types

    def __call__(self):
        for k, v in self.system_types:
            while True:
                cont = yield k
                if v or cont: break

class Allocator(object):
    """Allocates damage to a unit based on allocation rules."""

    def __init__(self, rules, choice):
        self.rules = [rule() for rule in rules] # set up generators
        self.choice = choice

    def find_target(self, unit, incident, damage_type):
        rule = self.choice(self.rules)
        system_type = rule.send(None)
        while True:
            valid_target = is_valid_target(system_type, incident, damage_type)
            systems = unit.find_systems(valid_target)
            if len(systems) > 0: return systems
            system_type = rule.send(True)

    def allocate(self, target):
        target.use_as('damage-target').apply_damage() 

class DamageAllocationChart(object):
    def __init__(self, name, rules):
	self.name = name
	self.rules = rules

    def __iter__(self):
	return iter(self.rules)

DAC_ship = DamageAllocationChart('DAC_ship', 
	   (RuleSet((('bridge', True), ('flag-bridge', True), ('sensor', True),
                     ('damage-control', True), ('aft-hull', True),
                     ('left-warp', False), ('transporter', False),
                     ('tractor', False), ('shuttle', False), ('lab', False),
                     ('forward-hull', False), ('right-warp', False),
                     ('excess-damage', False))),
            RuleSet((('drone', True), ('phaser', True), ('impulse', False),
                     ('left-warp', False), ('right-warp', False),
                     ('aft-hull', False), ('shuttle', False),
                     ('damage-control', True), ('center-warp', False),
                     ('lab', False), ('battery', False), ('phaser', False),
                     ('excess-damage', False))),
            RuleSet((('phaser', True), ('transporter', True),
                     ('right-warp', False), ('impulse', False),
                     ('forward-hull', False), ('aft-hull', False),
                     ('left-warp', False), ('apr', False), ('lab', False),
                     ('transporter', True), ('probe', False),
                     ('center-warp', False), ('excess-damage', False))),
            RuleSet((('right-warp', True), ('aft-hull', False),
                     ('cargo', False), ('battery', False), ('shuttle', False),
                     ('torpedo', True), ('left-warp', False),
                     ('impulse', False), ('right-warp', False),
                     ('tractor', False), ('probe', False), 
                     ('any-weapon', False), ('excess-damage', False))),
            RuleSet((('forward-hull', False), ('impulse', False), 
                     ('lab', False), ('left-warp', False), ('sensor', True), 
                     ('tractor', False), ('shuttle', False), 
                     ('right-warp', False), ('phaser', False),
                     ('transporter', False), ('battery', False), 
                     ('any-weapon', False), ('excess-damage', False))),
            RuleSet((('cargo', False), ('forward-hull', False), 
                     ('battery', False), ('center-warp', False), 
                     ('shuttle', False), ('apr', False), ('lab', False), 
                     ('phaser', False), ('any-warp', False), ('probe', False), 
                     ('aft-hull', False), ('any-weapon', False),
                     ('excess-damage', False))),
            RuleSet((('aft-hull', False), ('apr', False), ('shuttle', False),
                     ('right-warp', False), ('scanner', True), 
                     ('tractor', False), ('lab', False), ('left-warp', False), 
                     ('phaser', False), ('transporter', False), 
                     ('battery', False), ('any-weapon', False),
                     ('excess-damage', False))),
            RuleSet((('left-warp', True), ('forward-hull', False), 
                     ('cargo', False), ('battery', False), ('lab', False), 
                     ('drone', True), ('right-warp', False), 
                     ('impulse', False), ('left-warp', False),
                     ('tractor', False), ('probe', False), 
                     ('any-weapon', False), ('excess-damage', False))),
            RuleSet((('phaser', True), ('tractor', True), ('left-warp', False),
                     ('impulse', False), ('aft-hull', False), 
                     ('forward-hull', False), ('right-warp', False), 
                     ('apr', False), ('lab', False), ('transporter', False), 
                     ('probe', False), ('center-warp', False),
                     ('excess-damage', False))),
            RuleSet((('torpedo', True), ('phaser', True), ('impulse', False),
                     ('right-warp', False), ('left-warp', False), 
                     ('forward-hull', False), ('tractor', False), 
                     ('damage-control', True), ('center-warp', False),
                     ('lab', False), ('battery', False), ('phaser', False),
                     ('excess-damage', False))),
            RuleSet((('auxiliary-control', True), ('emergency-bridge', True), 
                     ('scanner', True), ('probe', True), 
                     ('forward-hull', True), ('right-warp', False),
                     ('transporter', False), ('shuttle', False),
                     ('tractor', False), ('lab', False), ('aft-hull', False), 
                     ('left-warp', False), ('excess-damage', False)))))
        
DAC_shuttle = DamageAllocationChart('DAC_shuttle', 
	      (RuleSet((('hull', False),)),))

def setup_registry(registry):
    registry.set(damage.name, damage, ResourceType)
    registry.set(phaser_damage.name, phaser_damage, ResourceType)
    
    registry.set(DAC_ship.name, DAC_ship, DamageAllocationChart) 
    registry.set(DAC_shuttle.name, DAC_shuttle, DamageAllocationChart)
