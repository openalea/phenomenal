import pytest
import os
import sys
import openalea.phenomenal.display as phm_display


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
    sc.add_actor_from_voxels(voxels_position=voxels_positions, voxels_size=4)


@skip_on_ci_non_linux
def test_display_scene_vertices_faces():
    sc = phm_display.Scene()
    vertices = ((0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    faces = ((0, 1, 2),)
    sc.add_actor_from_vertices_faces(vertices=vertices, faces=faces)
