import sys

from prjname.common.utils import settings_loader

sys.modules[__name__] = settings_loader.SettingsLoader("prjname.service1")
