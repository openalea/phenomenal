import numpy as np
import vtk

import openalea.phenomenal.display as phm_display
from openalea.phenomenal.display import Scene
from openalea.phenomenal.mesh import meshing
from openalea.phenomenal.object import (
    VoxelGrid,
    VoxelOrgan,
    VoxelSegment,
    VoxelSegmentation,
    VoxelSkeleton,
)

# ==============================================================================

POSITIONS = {(0, 0, 0), (4, 0, 0), (8, 0, 0), (12, 0, 0)}
POLYLINE = [(0, 0, 0), (4, 0, 0), (8, 0, 0), (12, 0, 0)]


def segment():
    return VoxelSegment(POLYLINE, set(POSITIONS), [{p} for p in POLYLINE])


def n_points(actor):
    return actor.GetMapper().GetInput().GetNumberOfPoints()


def test_actor_from_voxels_accepts_set_positions():
    actor = Scene.get_actor_from_voxels(VoxelGrid(set(POSITIONS), 4), color=(0, 1, 0))
    assert n_points(actor) > 0


def test_show_basic_record_voxel_grids(monkeypatch):
    grid = VoxelGrid(np.array(POLYLINE), 4)
    recorded = []

    def record_video(self, filename, elements, func):
        for element in elements:
            func(element)
        recorded.append(filename)

    monkeypatch.setattr(Scene, "record_video", record_video)
    monkeypatch.setattr(Scene, "set_camera", lambda self, **kwargs: None)
    phm_display.record_voxel_grids([grid], "video")
    assert recorded == ["video"]


def test_show_basic_show_voxel_grid(monkeypatch):
    actors = []
    monkeypatch.setattr(Scene, "show", lambda self, **kwargs: None)
    monkeypatch.setattr(Scene, "add_actor", lambda self, actor: actors.append(actor))
    phm_display.show_voxel_grid(VoxelGrid(np.array(POLYLINE), 4))
    assert n_points(actors[0]) > 0


def test_show_mesh_ignores_iso_values(monkeypatch):
    x, y, z = np.mgrid[-6:7, -6:7, -6:7]
    positions = np.argwhere(x**2 + y**2 + z**2 <= 25) * 4
    mesh = meshing(VoxelGrid(positions, 4))
    actors = []
    monkeypatch.setattr(Scene, "show", lambda self, **kwargs: None)
    monkeypatch.setattr(Scene, "add_actor", lambda self, actor: actors.append(actor))

    phm_display.show_mesh(mesh, color=(1, 0, 0))

    assert not actors[0].GetMapper().GetScalarVisibility()
    assert actors[0].GetProperty().GetColor() == (1, 0, 0)


def test_skeleton_actors():
    skeleton = VoxelSkeleton([segment()], 4)
    actors = phm_display.get_actors_from_skeleton(skeleton)
    assert all(isinstance(actor, vtk.vtkProp) for actor in actors)
    assert len(actors) > 0


def test_voxel_organ_actors():
    organ = VoxelOrgan("stem")
    organ.add_voxel_segment(set(POSITIONS), POLYLINE)
    actors, _ = phm_display.get_actors_from_voxel_organ(organ, 4)
    assert n_points(actors[0]) > 0


def test_segmentation_stem_mode_actors():
    organ = VoxelOrgan("stem")
    organ.add_voxel_segment(set(POSITIONS), POLYLINE)
    segmentation = VoxelSegmentation(4)
    segmentation.voxel_organs.append(organ)
    actors, _ = phm_display.get_actors_from_segmentation_stem_mode(segmentation)
    assert len(actors) == 1
    assert n_points(actors[0]) > 0
