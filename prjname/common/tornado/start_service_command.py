import abc

import cliff
import six
from tornado import httpserver
from tornado import ioloop


@six.add_metaclass(abc.ABCMeta)  # pylint: disable=R0903
class StartServiceCommand(cliff.command.Command):  # pylint: disable=too-few-public-methods
    """Start service command abstract implementation
    In the child class you MUST fill the service_application attribute with
    the Tornado application that you want to serve.
    Also you MUST override the get_description() method of
    cliff.command.Command
    """
    DEFAULT_PORT = 10000

    def __init__(self, app, app_args, service_application):
        self.service_application = service_application
        super(StartServiceCommand, self).__init__(app, app_args)

    def get_parser(self, prog_name):
        parser = super(StartServiceCommand, self).get_parser(prog_name)
        parser.add_argument("--port",
                            help="The port that the server will use",
                            type=int, default=self.DEFAULT_PORT)
        return parser

    def take_action(self, parsed_args):
        print "Listening at port {0}...".format(parsed_args.port)

        server = httpserver.HTTPServer(self.service_application, xheaders=True)
        server.bind(parsed_args.port)
        server.start()
        ioloop.IOLoop.current().start()
