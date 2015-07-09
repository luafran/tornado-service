import importlib
import itertools
import os

from prjname.common import exceptions


class SettingsLoader(object):  # pylint: disable=too-few-public-methods
    def __init__(self, settings_package, environment_name='MFS_ENV'):
        environment = os.environ.get(environment_name)
        if not environment:
            raise exceptions.GeneralInfoException(
                '{0} environment variable not found'.format(
                    environment_name))

        modules = [
            '{0}.{1}_settings'.format(settings_package, environment),
            '{0}.base_settings'.format(settings_package),
            'prjname.common.{0}_settings'.format(environment),
            'prjname.common.base_settings']

        self._settings_modules = []
        for module_name in modules:
            try:
                self._settings_modules.append(
                    importlib.import_module(module_name))
            except ImportError as ex:
                pass

    def __getattr__(self, name):
        setting_value = None
        all_modules = itertools.chain(self._settings_modules)
        while setting_value is None:
            try:
                module = all_modules.next()
                setting_value = getattr(module, name, None)
            except StopIteration:
                raise AttributeError(
                    "{0} was not found in settings".format(name))

        return setting_value
