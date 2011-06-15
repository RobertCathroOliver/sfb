import jolly.registry as _registry

registry = _registry.Registry()

import sfb.command
sfb.command.setup_registry(registry)
import sfb.firing_arc
sfb.firing_arc.setup_registry(registry)
import sfb.movement.turn_mode
sfb.movement.turn_mode.setup_registry(registry)
import sfb.damage
sfb.damage.setup_registry(registry)
import sfb.system
sfb.system.setup_registry(registry)
import sfb.unit
sfb.unit.setup_registry(registry)
