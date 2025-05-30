import importlib


class OptionalDependencyError(ImportError):
    def __init__(self, package_name: str, extra_name: str):
        message = (
            f"The optional dependency '{package_name}' is required for the '{extra_name}' feature.\n"
            f"Install it with: pip install your-package[{extra_name}]"
        )
        super().__init__(message)


def require_dependency(package_name: str, extra_name: str):
    try:
        mod = importlib.import_module(package_name)
    except ImportError:
        raise OptionalDependencyError(package_name, extra_name)
    return mod
