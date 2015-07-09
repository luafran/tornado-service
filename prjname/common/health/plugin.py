import abc
import six


@six.add_metaclass(abc.ABCMeta)  # pylint: disable=too-few-public-methods
class HealthPlugin(object):
    """Base class for Health plugins
    To add a new Health plugins you should use HealthPlugin as your base class
    and override the get_status() method.
    Then add to your setup.py a new entry_point to this class in the
    'prjname.health.plugins' namespace
        setuptools.setup(
            .
            entry_points={
                'prjname.health.plugins': [
                    'newHealthPlugin = path.to.new.command:NewHealthPlugin',
                ],
            },
        )
    """
    HEALTH_SEVERITY = (OK, WARNING, ERROR) = ((0, 'OK'), (1, 'WARNING'),
                                              (2, 'ERROR'))
    HEALTH_EXPOSURE = (LOW, MEDIUM, HIGH) = ('LOW', 'MEDIUM', 'HIGH')

    @abc.abstractmethod
    def get_status(self):
        """Returns the status of the service/plugin/etc that this class checks.
        This method should return a (HealthPlugin.HEALTH_SEVERITY, status)
        tuple, where the first element is the service/plugin/etc. health
        severity and the second element is a dictionary with this keys:
            {
                'name': 'Name of service/plugin/etc',
                'status': HealthPlugin.HEALTH_SEVERITY,
                'exposure': HealthPlugin.HEALTH_EXPOSURE
            }
        """
        raise NotImplementedError()
