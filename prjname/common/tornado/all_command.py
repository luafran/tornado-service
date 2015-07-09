import sys

import cliff
import stevedore
from tornado import httpserver
from tornado import ioloop


class AllCommand(cliff.command.Command):  # pylint: disable=too-few-public-methods
    def __init__(self, app, app_args):
        super(AllCommand, self).__init__(app, app_args)
        self.all_commands = stevedore.enabled.EnabledExtensionManager(
            namespace='prjname.services',
            invoke_on_load=False,
            check_func=lambda plugin: plugin.name != 'all',
        )

    def take_action(self, parsed_args):
        for command in self.all_commands:
            print "[{0}] listening at port {1}...".format(
                command.name, command.plugin.DEFAULT_PORT)

            server = httpserver.HTTPServer(
                sys.modules[command.plugin.__module__].APPLICATION,
                xheaders=True)
            server.bind(command.plugin.DEFAULT_PORT)
            server.start()

        ioloop.IOLoop.current().start()

    def get_description(self):
        return "All in one service"
