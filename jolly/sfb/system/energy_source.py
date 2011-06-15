from jolly.system import Prototype
from sfb.system.service import ResourceProducer, DamageTarget
from sfb import energy_type

class EnergySource(Prototype):
    """Defines systems that produce energy."""

    def __init__(self, name, energy_type, damaged_as):
        services = [ResourceProducer(energy_type),
                    DamageTarget(damaged_as)]
        super(EnergySource, self).__init__(name, services)

left_warp_engine = EnergySource('left-warp-engine', 
                                energy_type.warp_engine_energy,
                                ('left-warp', 'any-warp', 'excess-damage'))

center_warp_engine = EnergySource('center-warp-engine',
                                  energy_type.warp_engine_energy,
                                  ('center-warp', 'any-warp', 'excess-damage'))

right_warp_engine = EnergySource('right-warp-engine',
                                 energy_type.warp_engine_energy,
                                 ('right-warp', 'any-warp', 'excess-damage'))

impulse_engine = EnergySource('impulse-engine',
                              energy_type.impulse_energy,
                              ('impulse', 'excess-damage'))

AWR = EnergySource('AWR',
                   energy_type.warp_energy,
                   ('APR', 'excess-damage'))

APR = EnergySource('APR',
                   energy_type.energy,
                   ('APR', 'excess-damage'))
