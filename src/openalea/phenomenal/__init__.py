from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openalea.phenomenal")
except PackageNotFoundError:
    # package is not installed
    pass