from prjname.common.tornado.start_service_command import StartServiceCommand
from prjname.service1.tornado.application import APPLICATION


class Service1Command(StartServiceCommand):  # pylint: disable=too-few-public-methods
    DEFAULT_PORT = 10001

    def __init__(self, app, app_args):
        super(Service1Command, self).__init__(app, app_args, APPLICATION)

    def get_description(self):
        return "service1 service"
