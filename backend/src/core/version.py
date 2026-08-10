from functools import cache
from importlib.metadata import version


@cache
def get_app_version() -> str:
    return version("lumiere-backend")
