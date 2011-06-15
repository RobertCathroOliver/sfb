from jolly.resource import ResourceType
from sfb import registry

energy = ResourceType('energy')
impulse_energy = ResourceType('impulse', [energy])
warp_energy = ResourceType('warp', [energy])
warp_engine_energy = ResourceType('warp-engine', [energy, warp_energy])

registry.set(energy.name, energy, ResourceType)
registry.set(impulse_energy.name, energy, ResourceType)
registry.set(warp_energy.name, warp_energy, ResourceType)
registry.set(warp_engine_energy.name, warp_engine_energy, ResourceType)

