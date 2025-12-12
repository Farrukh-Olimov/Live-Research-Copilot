import importlib
from logging import getLogger
import pkgutil

logger = getLogger(__name__)


def auto_import_datasource_schemas():
    """Automatically imports all schema modules in this package."""
    for module_info in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
        module_name = module_info.name
        if module_name.endswith("schema"):
            logger.info(f"Importing {module_name}")
            importlib.import_module(module_name)


auto_import_datasource_schemas()
