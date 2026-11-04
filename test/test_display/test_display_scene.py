import numpy as np
import pytest
import os
import sys
from PIL import Image
from vtkmodules.util.numpy_support import vtk_to_numpy
import openalea.phenomenal.display as phm_display
from openalea.phenomenal.object import VoxelGrid

POLYLINES = [[(0, 0, 0), (10, 0, 0), (10, 10, 0)], [(0, 0, 20), (0, 0, 30)]]


# rendering needs a graphics context, which CI machines may not provide
@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Needs rendering")
def test_screenshot_magnification(tmp_path):
    scene = phm_display.Scene()
    scene.add_actor_from_polylines(POLYLINES, colors=(1, 0, 0))
    scene.reset_camera()

    sizes = []
    for magnification in (1, 2):
        filename = tmp_path / f"scene_{magnification}.png"
        scene.screenshot(str(filename), magnification=magnification)
        with Image.open(filename) as image:
            sizes.append(image.size)
            pixels = np.asarray(image.convert("RGB"))

    assert sizes[1] == (2 * sizes[0][0], 2 * sizes[0][1])
    # white background, and the polylines in red
    assert (pixels == [255, 255, 255]).all(axis=-1).any()
    assert ((pixels[..., 0] > 200) & (pixels[..., 1] < 100)).any()


def tube_of(actor):
    return actor.GetMapper().GetInput()


def test_actor_from_polylines_geometry():
    actor = phm_display.Scene.get_actor_from_polylines(POLYLINES, radius=1)
    tube = tube_of(actor)
    assert tube.GetNumberOfCells() > 0
    xmin, xmax, ymin, ymax, zmin, zmax = tube.GetBounds()
    np.testing.assert_allclose([xmin, xmax, zmin, zmax], [-1, 11, -1, 30], atol=0.01)
    assert ymax == pytest.approx(10, abs=0.01)


def test_actor_from_polylines_one_color_per_polyline():
    actor = phm_display.Scene.get_actor_from_polylines(
        POLYLINES, colors=[(1, 0, 0), (0, 0, 1)]
    )
    colors = vtk_to_numpy(tube_of(actor).GetCellData().GetScalars())
    assert len(colors) == tube_of(actor).GetNumberOfCells()
    np.testing.assert_array_equal(np.unique(colors, axis=0), [[0, 0, 255], [255, 0, 0]])


def test_actor_from_polylines_empty():
    actor = phm_display.Scene.get_actor_from_polylines([])
    assert tube_of(actor).GetNumberOfPoints() == 0


def test_actor_from_polylines_rejects_wrong_number_of_colors():
    with pytest.raises(ValueError):
        phm_display.Scene.get_actor_from_polylines(POLYLINES, colors=[(1, 0, 0)] * 3)


def test_show_polylines(monkeypatch):
    actors = []
    monkeypatch.setattr(phm_display.Scene, "show", lambda self, **kwargs: None)
    monkeypatch.setattr(phm_display.Scene, "add_actor", lambda self, actor: actors.append(actor))
    phm_display.show_polylines(POLYLINES, colors=(0, 1, 0))
    assert tube_of(actors[0]).GetNumberOfPoints() > 0


skip_on_ci_non_linux = pytest.mark.skipif(
    os.environ.get("CI") == "true" and not sys.platform.startswith("linux"),
    reason="Skipped on CI except on Linux"
)

@skip_on_ci_non_linux
def test_display_scene_text():
    sc = phm_display.Scene()
    sc.add_actor_from_text(text="Test")
    actor = sc.get_actor_from_text(text="Test")
    sc.add_actor(actor)


@skip_on_ci_non_linux
def test_display_scene_plane():
    sc = phm_display.Scene()
    sc.add_actor_from_plane(center=(1, 1, 1), normal=(0, 0, 1))


@skip_on_ci_non_linux
def test_display_scene_ball():
    sc = phm_display.Scene()
    sc.add_actor_from_ball_position(position=(1, 1, 1))


@skip_on_ci_non_linux
def test_display_scene_arrow():
    sc = phm_display.Scene()
    sc.add_actor_from_arrow_vector(start_point=(0, 0, 0), end_point=(1, 0, 1))


@skip_on_ci_non_linux
def test_display_scene_voxels():
    sc = phm_display.Scene()
    voxels_positions = ((0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    voxels_size = 4
    sc.add_actor_from_voxels(VoxelGrid(voxels_positions, voxels_size))

