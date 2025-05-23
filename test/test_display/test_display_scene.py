import pytest

import openalea.phenomenal.display as phm_display


@pytest.mark.skip()
def test_display_scene_text():
    sc = phm_display.Scene()
    sc.add_actor_from_text(text="Test")
    actor = sc.get_actor_from_text(text="Test")
    sc.add_actor(actor)


@pytest.mark.skip()
def test_display_scene_plane():
    sc = phm_display.Scene()
    sc.add_actor_from_plane(center=(1, 1, 1), normal=(0, 0, 1))


@pytest.mark.skip()
def test_display_scene_ball():
    sc = phm_display.Scene()
    sc.add_actor_from_ball_position(position=(1, 1, 1))


@pytest.mark.skip()
def test_display_scene_arrow():
    sc = phm_display.Scene()
    sc.add_actor_from_arrow_vector(start_point=(0, 0, 0), end_point=(1, 0, 1))


@pytest.mark.skip()
def test_display_scene_voxels():
    sc = phm_display.Scene()
    voxels_positions = ((0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    sc.add_actor_from_voxels(voxels_position=voxels_positions, voxels_size=4)


@pytest.mark.skip()
def test_display_scene_vertices_faces():
    sc = phm_display.Scene()
    vertices = ((0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    faces = ((0, 1, 2),)
    sc.add_actor_from_vertices_faces(vertices=vertices, faces=faces)
