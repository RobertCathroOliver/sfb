from jolly.command import CommandTemplate, FormalArgument, Command
from jolly.core import Game

from sfb.chrono import Duration, IMPULSES_PER_TURN

class TurnSetup(CommandTemplate):

    def __init__(self):
        arguments = FormalArgument('game', Game, upfront=True)
        super(TurnSetup, self).__init__('turn-setup', 'turn-setup', [])

    def execute(self, command, env=None):
        game = command.arguments['game']
        # insert mandatory commands for this turn
        for unit in game.units:
            for c in unit.exposed_commands:
                if not c.required: 
		    continue
                base_moment = game.sequence_of_play.get_moment(c.step) + Duration(command.time.turn)
                arguments = {'unit' : unit}
                if base_moment.impulse is None:
                    cmd = Command(self, c, base_moment, arguments)
                    cmd.insert_into_queue(command.queue, env)
                else:
                    for i in range(IMPULSES_PER_TURN):
                        moment = base_moment + Duration(0, i)
                        cmd = Command(self, c, moment, arguments)
                        cmd.insert_into_queue(command.queue, env)
 
        # insert next turn-setup command for next turn
        moment = command.time + Duration(1)
        cmd = Command(self, self, moment, command.arguments)
        cmd.insert_into_queue(command.queue)

	return [command.create_action('turn-setup', game, 'Turn setup')]
