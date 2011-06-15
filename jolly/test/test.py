import sys
sys.path.insert(0, '/Users/robert/jolly')

# setup
import jolly.map
import sfb.map
import sfb.chrono
import sfb.unit
import sfb.movement
import jolly.core
import jolly.command
import sfb.util
from sfb.command import registry as commands

speed_plot1 = sfb.movement.make_speed_plot(6)
position1 = jolly.map.Position(sfb.map.Location((4, 5)), sfb.map.compass.get('A'))
shuttle1 = sfb.unit.admin_shuttle.create_system(1, None, {'speed-plot' : speed_plot1, 'position' : position1 })
player1 = jolly.core.Player('player-1', [shuttle1])

speed_plot2 = sfb.movement.make_speed_plot(6)
position2 = jolly.map.Position(sfb.map.Location((4, 1)), sfb.map.compass.get('D'))
shuttle2 = sfb.unit.admin_shuttle.create_system(2, None, {'speed-plot' : speed_plot2, 'position' : position2 })
player2 = jolly.core.Player('player-2', [shuttle2])

map = jolly.map.Map((10, 6))
token1 = jolly.map.Token(shuttle1, map, position1)
token1.place()
token2 = jolly.map.Token(shuttle2, map, position2)
token2.place()

game = jolly.core.Game(sfb.chrono.SOP, map, [player1, player2], sfb.util.choice)

cmd = jolly.command.Command(None, commands['turn-setup'], sfb.chrono.SOP.get_moment('turn-setup'), {'game' : game})
game.insert_into_queue(cmd)
