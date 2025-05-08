import importlib.util

class OptionalDependencyError(ImportError):
    def __init__(self, package_name: str, extra_name: str):
        message = (
            f"The optional dependency '{package_name}' is required for the '{extra_name}' feature.\n"
            f"Install it with: pip install your-package[{extra_name}]"
        )
        super().__init__(message)

def require_dependency(package_name: str, extra_name: str):
    if importlib.util.find_spec(package_name) is None:
        raise OptionalDependencyError(package_name, extra_name)
