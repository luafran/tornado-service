import stevedore

from tornado import gen

from prjname.common import version
from prjname.common.health.plugin import HealthPlugin


class HealthMonitor(object):  # pylint: disable=R0903
    def __init__(self):
        self.plugins = stevedore.extension.ExtensionManager(
            namespace='prjname.health.plugins',
            invoke_on_load=True,
        )

    @gen.coroutine
    def get_status(self, include_details=False):
        service_health = HealthPlugin.OK

        plugin_status = []
        for plugin in self.plugins:
            health, status = yield plugin.obj.get_status()
            service_health = (health if health > service_health
                              else service_health)
            plugin_status.append(status)

        # health severity's status could be OK, WARNING or ERROR
        service_status = [{
            'name': 'systemHealth',
            'status': service_health[1],
            'exposure': HealthPlugin.HIGH
        }]

        status = []
        if include_details:
            status.extend(service_status)
            status.extend(plugin_status)

        raise gen.Return((service_health, status, version.get_version()))
