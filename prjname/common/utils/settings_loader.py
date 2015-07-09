import collections
import importlib
import itertools
import os

from miramar.common import exceptions


class SettingsLoader(object):  # pylint: disable=too-few-public-methods
    FROM_ENVIRONMENT = 'environment'

    def __init__(self, settings_package, mfs_environment_name='MFS_ENV',
                 environment_prefix='MFS', modules_lazy_load=True):
        self._mfs_environment = os.environ.get(mfs_environment_name)
        if not self._mfs_environment:
            raise exceptions.GeneralInfoException(
                '{0} environment variable not found'.format(
                    mfs_environment_name))
        self._settings_package = settings_package
        self._environment_prefix = environment_prefix

        self._settings_modules = []
        if not modules_lazy_load:
            self._lazy_module_import()

    def _lazy_module_import(self):
        modules = [
            '{0}.{1}_settings'.format(self._settings_package,
                                      self._mfs_environment),
            '{0}.base_settings'.format(self._settings_package),
            'miramar.common.{0}_settings'.format(self._mfs_environment),
            'miramar.common.base_settings']

        self._settings_modules = []
        for module_name in modules:
            try:
                self._settings_modules.append(
                    importlib.import_module(module_name))
            except ImportError:
                pass

    def __getattr__(self, name):
        setting_value = os.environ.get(
            "{0}_{1}".format(self._environment_prefix, name.upper()))

        if not setting_value:
            if not self._settings_modules:
                self._lazy_module_import()

            all_modules = itertools.chain(self._settings_modules)
            while setting_value is None:
                try:
                    module = all_modules.next()
                    setting_value = getattr(module, name, None)
                except StopIteration:
                    raise AttributeError(
                        "{0} was not found in settings".format(name))

        return setting_value

    def actual_settings(self):
        settings = collections.defaultdict(lambda: {'value': '',
                                                    'from': ''})

        if not self._settings_modules:
            self._lazy_module_import()

        for module in reversed(self._settings_modules):
            display_settings = getattr(module, 'DISPLAY_SETTINGS', None)
            if display_settings:
                names_values_module = [(name, getattr(module, name), module)
                                       for name in display_settings
                                       if getattr(module, name, None)]
                for name, value, module in names_values_module:
                    environment_name = "{0}_{1}".format(
                        self._environment_prefix, name.upper())

                    settings[name]['value'] = os.environ.get(environment_name,
                                                             value)
                    settings[name]['from'] = (
                        self.FROM_ENVIRONMENT if environment_name in os.environ
                        else module.__name__.split('.')[-1])

        return dict(settings)
