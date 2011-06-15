import jolly.system
from sfb import registry

from energy_source import (left_warp_engine, center_warp_engine,
                          right_warp_engine, impulse_engine, AWR, APR)

from hull import (forward_hull, center_hull, aft_hull, shuttle_hull)

from phaser import (phaser1, phaser2, phaser3, phaser4, phaserG,
                    shuttle_phaser1, shuttle_phaser2, 
                    shuttle_phaser3, shuttle_phaserG)

def setup_registry(registry):
    registry.set(left_warp_engine.name, left_warp_engine, jolly.system.Prototype)
    registry.set(center_warp_engine.name, center_warp_engine, jolly.system.Prototype)
    registry.set(right_warp_engine.name, right_warp_engine, jolly.system.Prototype)
    registry.set(impulse_engine.name, impulse_engine, jolly.system.Prototype)
    registry.set(AWR.name, AWR, jolly.system.Prototype)
    registry.set(APR.name, APR, jolly.system.Prototype)
    registry.set(forward_hull.name, forward_hull, jolly.system.Prototype)
    registry.set(center_hull.name, center_hull, jolly.system.Prototype)
    registry.set(aft_hull.name, aft_hull, jolly.system.Prototype)
    registry.set(shuttle_hull.name, shuttle_hull, jolly.system.Prototype)
    registry.set(phaser1.name, phaser1, jolly.system.Prototype)
    registry.set(phaser2.name, phaser2, jolly.system.Prototype)
    registry.set(phaser3.name, phaser3, jolly.system.Prototype)
    registry.set(phaser4.name, phaser4, jolly.system.Prototype)
    registry.set(phaserG.name, phaserG, jolly.system.Prototype)
    registry.set(shuttle_phaser1.name, shuttle_phaser1, jolly.system.Prototype)
    registry.set(shuttle_phaser2.name, shuttle_phaser2, jolly.system.Prototype)
    registry.set(shuttle_phaser3.name, shuttle_phaser3, jolly.system.Prototype)
    registry.set(shuttle_phaserG.name, shuttle_phaserG, jolly.system.Prototype)
            
