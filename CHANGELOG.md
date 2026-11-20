# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
* `Scene.get_actor_from_polylines`, `Scene.add_actor_from_polylines` and `show_polylines` to display polylines with VTK.
* `read_pointcloud` to load the point positions of a text file.
* A `depth` option on `get_projection`, to get (u, v, depth) coordinates.

### Changed
* Runtime and documentation dependencies are declared with conda (`conda/run_deps.yml`, `doc/doc_deps.yml`) instead of `pyproject.toml`, which no longer has runtime dependencies or extras. Read the Docs now documents the published package, and the installation instructions are only in `README.md`. Binder installs the notebook data and pandas instead of ipyvolume.
* `tracking.display.plot_polylines` uses VTK instead of PlantGL, and blocks until its window is closed.
* `segment_reduction` is written in NumPy and uses less memory. The package has no more compiled code, and does not need a compiler to build.
* Multi-view reconstruction filters voxels behind the camera plane, and needs projections with depth: use `get_projection(..., depth=True)`, as `as_image_views` does. Projections without depth raise a `ValueError`.
* `voxels_is_visible_in_image`: `inclusive` now defaults to `True`.
* `get_bounding_box_voxel_projected` takes projected voxel corners (see `project_voxels`), and `integral_image_hits` no longer takes the image size.

### Fixed
* `Display.screenshot`, and the `screenshot_filename` option of the `show_*` functions, with recent VTK versions.
* `tolerant_reconstruction` and `multi_tolerant_reconstruction` crashed with their default `clear_outside`, which is now `True`.
* `project_voxels_position_on_image` crashed on voxels whose visible part is a single line of pixels.
* `erode_dilate`, `dilate_erode` and `close` with a `mask` turned the background outside the mask white: since 1.10.0 they used NumPy arithmetic, which wraps around on `uint8` images (0 - 1 = 255). They use OpenCV again, with saturated arithmetic and the original `kernel_shape` meaning and defaults.
* `phenoarch_side_binarization` converts its RGB image to HSV with OpenCV (`cv2.COLOR_RGB2HSV`), so that the hue is in [0, 180] like `hsv_min` and `hsv_max`: since 1.10.0 it used PIL, whose hue is in [0, 255]. The median filter is `cv2.medianBlur` again, and the two binary images are added with saturation (no more 254 values).
* The Binarization tutorial and the PhenoArch wralea routines converted the RGB images of `read_image`/`data` to HSV as if they were BGR (`cv2.COLOR_BGR2HSV`, swapping red and blue); they use `cv2.COLOR_RGB2HSV`. On the tutorial images this changes the binarizations by less than 1%.

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