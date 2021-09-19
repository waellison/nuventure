"""Driver module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

from nuventure import ERROR_STR, dbg_print, func_name, nv_print
from nuventure.errors import NVParseError, NVBadTargetError, \
    NVBadArgError, NVNoArgError, NVGameStateError
from nuventure.world import NVWorld
from nuventure.actor import NVActor
from nuventure.parser import NVParser
from nuventure.verb_callbacks import do_quit


class NVGame:
    """
    NVGame is a singleton class for running the Nuventure engine.
    It runs the input loop and handles some outlier parse errors.
    """

    def __init__(self, path):
        self.world = NVWorld(self, path)
        self.start_node = self.world.nodes["ORIGIN"]
        self.player = NVActor(self.world, self.start_node)
        self.world.add_actor(self.player)
        self.parser = NVParser()

    def run(self):
        """Run the game by rendering the player's starting location
        and then starting the input loop.
        """
        self.player.location.render()

        while True:
            result = self._do_input_loop()
            if result:
                self.world.do_world_tic()

    def _do_parse_error(self):
        """Issue a parse error."""
        last = self.parser.last_command
        if last:
            self.parser.error(last.split(" ")[0])
        else:
            nv_print(ERROR_STR)

    def _do_input_loop(self):
        """Accept input from the user and process it."""
        self.player.location.visitedp = True

        try:
            verb = self.parser.read_command(self.player)
        except NotImplementedError:
            nv_print("this action is not implemented yet")
        except (KeyboardInterrupt, EOFError):
            do_quit()
        except NVParseError:
            return False
        else:
            if verb:
                try:
                    result = verb.invoke()
                except (NVBadArgError, NVBadTargetError) as ex:
                    self.parser.rich_error(ex.verb, ex.et_key, ex.arg)
                except NVNoArgError as ex:
                    self.parser.rich_error(ex.verb, "noargs")
                except NVGameStateError as ex:
                    self.parser.rich_error(ex.verb, "badstate")
                else:
                    return result
            else:
                self._do_parse_error()
                return False
