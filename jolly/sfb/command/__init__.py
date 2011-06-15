from jolly.command import CommandTemplate
from sfb.command.move import Move
from sfb.command.direct_fire import (DecideDirectFire, 
                                     AnnounceDirectFire,
                                     ResolveOtherWeapons)
from sfb.command.speed import (AnnounceInitialSpeed, 
                               AnnounceSpeedChange,
                               ShuttleDetermineInitialSpeed, 
                               EmergencyDeceleration,
                               AnnounceEmergencyDeceleration)
from sfb.command.damage import AllocateDamage
from sfb.command.setup import TurnSetup

def setup_registry(registry):
    registry.set('move', Move(), CommandTemplate)
    registry.set('decide-direct-fire', DecideDirectFire(), CommandTemplate)
    registry.set('announce-direct-fire', AnnounceDirectFire(), CommandTemplate)
    registry.set('resolve-other-weapons', ResolveOtherWeapons(), CommandTemplate)
    registry.set('announce-initial-speed', AnnounceInitialSpeed(), CommandTemplate)
    registry.set('announce-speed-change', AnnounceSpeedChange(), CommandTemplate)
    registry.set('shuttle-determine-initial-speed', ShuttleDetermineInitialSpeed(), CommandTemplate)
    registry.set('emergency-deceleration', EmergencyDeceleration(), CommandTemplate)
    registry.set('announce-emergency-deceleration', AnnounceEmergencyDeceleration(), CommandTemplate)
    registry.set('allocate-damage', AllocateDamage(), CommandTemplate)
    registry.set('turn-setup', TurnSetup(), CommandTemplate)
