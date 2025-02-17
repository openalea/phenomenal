# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
* A `CITATION.cff` file

### Changed
* Unifying docstring style to follow [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html) style.
* Reducing OpenCV dependencies.

### Fixed
* Orientation of meshes in notebook.

## [1.9.4]
### Added

- A `pyproject.toml` file.
- This CHANGELOG.md file.
- Phenotrack citation in [README.md](./README.md) (#44). 
- [OpenAlea svg](./doc/_static/openalea_web.svg) logo for documentation.
- More test for the test suite.

### Changed

- The documentation configuration file `conf.py` with [OpenAlea Guidelines](https://openalea.readthedocs.io/en/latest/development/guidelines.html).
- Modernized the test suite.
- Compatibility with numpy 2.0.
- Updated code to respect guidelines.
- Formating source files with [ruff](https://docs.astral.sh/ruff/).

### Fixed

- Updating skan function to more recent versions.
- Removed warning of test files saved with python 2 by saving them again with python 3.
- Fixing location of data for notebook examples.