import importlib
from logging import getLogger
import os
import pkgutil

logger = getLogger(__name__)
imported = set()


def auto_import_datasource_schemas():
    """Automatically imports all schema modules in this package."""
    for module_info in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
        module_name = module_info.name
        module_init = module_name.replace(".", "/")
        module_init = os.path.join(module_init, "__init__.py")
        if module_name not in imported and os.path.exists(module_init):
            # if module_name.endswith("schema"):
            logger.info(f"Importing {module_name}")
            importlib.import_module(module_name)
            imported.add(module_name)
