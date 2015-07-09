"""
Script to start Miramar services
"""
import argparse
import cProfile as profile
import functools
import pstats
import signal
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
from tornado import ioloop
from tornado import web


class RunService(App):  # pylint: disable=too-few-public-methods
    """Miramar run service command line application.
    In order to add a new service to this command line application, you need
    to create a class that inhitered from cliff.Command:
        import cliff


        class NewCommand(cliff.command.Command):
            def get_description(self):
                return "A New command"

            def get_parser(self, prog_name):
                parser = super(NewCommand, self).get_parser(prog_name)
                parser.add_argument('aParameter', nargs='?', default='.')
                return parser

            def take_action(self, parsed_args):
                some = SomeClass()
                some.execute()

    Then add to your setup.py a new entry_point to this class in the
    'prjname.service' namespace
        setuptools.setup(
            .
            entry_points={
                'prjname.services': [
                    'newCommand = path.to.new.command:NewCommand',
                ],
            },
        )
    """
    def __init__(self):
        super(RunService, self).__init__(
            description='Miramar services',
            version='1.0',
            command_manager=CommandManager('prjname.services'),)


def shutdown():
    ioloop.IOLoop.current().stop()


def sig_handler(sig, frame):  # pylint: disable=unused-argument
    ioloop.IOLoop.current().add_callback(shutdown)


def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--profile', help="Enable profiling",
                        action='store_const', const=True, default=False)
    parser.add_argument('--output-file', type=str,
                        help="The file to store the profiling output",
                        default="prjname-{0}.prof")
    parsed_args, remaining_args = parser.parse_known_args()

    profiler = profile.Profile()

    def _profile_patch(execute):
        @functools.wraps(execute)
        def inner(self, transforms, *args, **kwargs):
            if 'profile' in self.request.arguments:
                profile_filter = self.request.arguments.pop('profile')
                result = profiler.runcall(execute, self, transforms,
                                          *args, **kwargs)
                profile_stats = pstats.Stats(profiler)
                if 'prjname' in profile_filter:
                    profile_stats.stats = (
                        {k: v for k, v in profile_stats.stats.iteritems()
                         if '_pkg/prjname/' in k[0]})

                service = self.__module__.split('.')
                service = service[1] if len(service) >= 2 else service[0]
                profile_stats.dump_stats(parsed_args.output_file.format(
                    service))
            else:
                result = execute(self, transforms, *args, **kwargs)

            return result

        return inner

    if parsed_args.profile:
        old_execute = web.RequestHandler._execute  # pylint: disable=protected-access
        web.RequestHandler._execute = _profile_patch(old_execute)  # pylint: disable=protected-access

    myapp = RunService()
    return myapp.run(remaining_args)

if __name__ == '__main__':
    sys.exit(main())
