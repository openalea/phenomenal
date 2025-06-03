import importlib
from importlib.metadata import metadata
this_package = 'openalea.phenomenal'


def extra_map(package):
    """return a {deps: extra_label} mapping of optional deps found in package"""
    meta = metadata(package).json
    deps = meta.get('requires_dist', [])
    pkg_extra_map = {}
    for dep in deps:
        if ';' in dep:
            pkg, extra_part = dep.split(';', 1)
            pkg = pkg.strip()
            extra = extra_part.strip().replace('extra == ', '').strip('"').strip("'")
        else:
            pkg = dep.strip()
            extra = ''
        pkg_extra_map[pkg] = extra
    return pkg_extra_map


class OptionalDependencyError(ImportError):
    def __init__(self, package_name: str):
        extras = extra_map(this_package)
        extra_name = extras.get(package_name.split('.')[0], 'not_defined_as_extra')
        message = (
            f"The '{extra_name}' extra feature is required for the optional dependency '{package_name}'.\n"
            f"Install it with: pip install {this_package}[{extra_name}]"
        )
        super().__init__(message)


def require_dependency(package_name: str):
    """
    User-friendly import of extra deps

    Args:
        package_name: the name of the extra package required
    """
    try:
        mod = importlib.import_module(package_name)
    except ImportError:
        raise OptionalDependencyError(package_name)
    return mod
