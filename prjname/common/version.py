from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

UNKNOWN_VERSION = 'UNKNOWN'


def _get_distribution_name():
    return "prjname-service1"


def get_version():
    try:
        return get_distribution(_get_distribution_name()).version
    except DistributionNotFound:
        return UNKNOWN_VERSION
