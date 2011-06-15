import jolly.system
from sfb import registry

from shuttle import admin_shuttle

def setup_registry(registry):
    registry.set(admin_shuttle.name, admin_shuttle, jolly.system.Prototype)
