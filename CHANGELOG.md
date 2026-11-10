# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
* `Scene.get_actor_from_polylines`, `Scene.add_actor_from_polylines` and `show_polylines` to display polylines with VTK.
* `read_pointcloud` to load the point positions of a text file.

### Changed
* Dependencies are declared in `conda/` (`run_deps.yml`, `doc_deps.yml`, `meta.yaml`, `environment.yml`) instead of `pyproject.toml`, which no longer has runtime dependencies or extras. Read the Docs now documents the published package.
* `tracking.display.plot_polylines` uses VTK instead of PlantGL, and blocks until its window is closed.
* `segment_reduction` is written in NumPy and uses less memory. The package has no more compiled code, and does not need a compiler to build.

### Fixed
* `Display.screenshot`, and the `screenshot_filename` option of the `show_*` functions, with recent VTK versions.

## [1.9.5]
### Added
* A `CITATION.cff` file

### Changed
* Unifying docstring style to follow [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html) style.
* Reducing OpenCV dependencies.
* The `setup.py` only handles the Cython extensions. The rest is handled by the `pyproject.toml`. Phenomenal is now installable in [venv](https://docs.python.org/3/library/venv.html)

### Fixed
* Orientation of meshes in notebook.
* Phenotrack citation's formatting in `README.md`.

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