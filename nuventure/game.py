"""

"""
from nuventure.world import NVWorld
from nuventure.actor import NVActor
from nuventure.parser import NVParser
from nuventure.verb_callbacks import do_quit


class NVGame:
    def __init__(self, path):
        self.world = NVWorld(path)
        self.start_node = self.world.nodes["ORIGIN"]
        self.player = NVActor(self.world, self.start_node)
        self.world.add_actor(self.player)
        self.parser = NVParser()

    def run(self):
        self.player.location.render()

        while True:
            self._do_input_loop()

    def _do_parse_error(self):
        last = self.parser.last_command
        if len(last):
            self.parser.error(last.split(" ")[0])

    def _do_input_loop(self):
        self.player.location.visitedp = True
        print("")

        try:
            verb = self.parser.read_command(self.player)
        except NotImplementedError:
            print("this action is not implemented yet")
        except (KeyboardInterrupt, EOFError):
            do_quit()
        else:
            if verb:
                result = verb.invoke()
            else:
                result = False

            if not result:
                self._do_parse_error()
