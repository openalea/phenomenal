# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
import copy
import pickle
from pathlib import Path

import numpy as np
import pytest

from openalea.phenomenal.data import voxel_grid
from openalea.phenomenal.mesh import meshing, voxelization
from openalea.phenomenal.object import Image3D, Mesh, VoxelGrid

# ==============================================================================

VERTICES = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1.0]])
FACES = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 3, 2]])
COLORS = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255], [9, 9, 9]], dtype=np.uint8)
VIDS = np.array([7, 8, 9, 10])


def sphere_grid(voxels_size=4):
    x, y, z = np.mgrid[-6:7, -6:7, -6:7]
    positions = np.argwhere(x**2 + y**2 + z**2 <= 25) * voxels_size
    return VoxelGrid(positions, voxels_size)


def test_empty_mesh():
    mesh = Mesh()
    assert mesh.vertices.shape == (0, 3)
    assert mesh.faces.shape == (0, 3)
    assert mesh.colors.shape == (0, 3)
    assert mesh.normals.shape == (0, 3)
    assert mesh.centers.shape == (0, 3)
    assert mesh.triangle_areas.shape == (0,)


def is_closed(mesh):
    edges = np.sort(mesh.faces[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return len(counts) > 0 and np.all(counts == 2)


def test_meshing_solid_block():
    # voxels filling their bounding box touch all the borders of the image
    voxels_size = 4
    positions = np.argwhere(np.ones((3, 3, 3))) * voxels_size + (10, 20, 30)
    mesh = meshing(VoxelGrid(positions, voxels_size))

    assert is_closed(mesh)
    assert len(mesh.normals) == len(mesh.faces)
    # the iso-surface lies halfway between the outer voxels and the empty layer
    np.testing.assert_allclose(mesh.vertices.min(axis=0), (8, 18, 28))
    np.testing.assert_allclose(mesh.vertices.max(axis=0), (20, 30, 40))


@pytest.mark.parametrize("smoothing_iteration, reduction", [(2, 0.0), (0, 0.5), (2, 0.5)])
def test_meshing_solid_block_with_filters(smoothing_iteration, reduction):
    positions = np.argwhere(np.ones((3, 3, 3)))
    mesh = meshing(
        VoxelGrid(positions, 1),
        smoothing_iteration=smoothing_iteration,
        reduction=reduction,
    )
    assert is_closed(mesh)


@pytest.mark.parametrize("smoothing_iteration, reduction", [(0, 0.0), (2, 0.0), (0, 0.5), (2, 0.5)])
@pytest.mark.parametrize("voxels", [[(5, 6, 7)], [(0, 0, 0), (1, 0, 0)]])
def test_meshing_very_small_grids(voxels, smoothing_iteration, reduction):
    mesh = meshing(
        VoxelGrid(voxels, 1),
        smoothing_iteration=smoothing_iteration,
        reduction=reduction,
    )
    assert len(mesh.faces) > 0
    assert is_closed(mesh)


def test_voxelization_of_single_voxel():
    grid = voxelization(meshing(VoxelGrid([(5, 6, 7)], 2)), voxels_size=2)
    np.testing.assert_allclose(grid.voxels_position, [(5, 6, 7)])


def test_meshing_flat_block():
    # a single layer of voxels used to have no thickness in the image
    positions = np.argwhere(np.ones((3, 3, 1)))
    mesh = meshing(VoxelGrid(positions, 1))
    assert is_closed(mesh)
    np.testing.assert_allclose(mesh.vertices.min(axis=0), (-0.5, -0.5, -0.5))
    np.testing.assert_allclose(mesh.vertices.max(axis=0), (2.5, 2.5, 0.5))


def test_voxelization_of_solid_block():
    positions = np.argwhere(np.ones((3, 3, 3)))
    grid = voxelization(meshing(VoxelGrid(positions, 1)), voxels_size=1)
    assert len(grid) == 27


def test_meshing_closes_surface_on_real_plant():
    plant = Path(__file__).parents[1] / "data" / "plant_1"
    grid = voxel_grid(plant, voxels_size=16)
    mesh = meshing(grid)
    assert is_closed(mesh)

    # a closed surface gives back the voxels it was built from
    voxelized = voxelization(mesh, voxels_size=16)
    assert set(map(tuple, voxelized.voxels_position)) == set(map(tuple, grid.voxels_position))


def test_iso_values_are_not_colors():
    mesh = meshing(sphere_grid())
    assert mesh.GetPointData().GetScalars() is not None
    assert mesh.colors.shape == (0, 3)


def test_ply_keeps_colors(tmp_path):
    filename = str(tmp_path / "mesh.ply")
    Mesh.from_pymesh(VERTICES, FACES, colors=COLORS).write_ply(filename)
    mesh = Mesh.from_ply(filename)
    np.testing.assert_array_equal(mesh.colors, COLORS)

    # colors read from a ply have another array name and must be kept as well
    filename = str(tmp_path / "again.ply")
    mesh.write_ply(filename)
    np.testing.assert_array_equal(Mesh.from_ply(filename).colors, COLORS)


def test_ply_without_colors(tmp_path):
    filename = str(tmp_path / "mesh.ply")
    meshing(sphere_grid()).write_ply(filename)
    assert Mesh.from_ply(filename).colors.shape == (0, 3)


@pytest.mark.parametrize(
    "colors, vids", [(None, None), (COLORS, None), (None, VIDS), (COLORS, VIDS)]
)
def test_drc_round_trip(tmp_path, colors, vids):
    pytest.importorskip("DracoPy")
    filename = str(tmp_path / "mesh.drc")
    Mesh.from_pymesh(VERTICES, FACES, colors=colors, vids=vids).to_drc(
        filename, quantization_bits=0, preserve_order=True
    )
    mesh = Mesh.from_drc(filename)

    np.testing.assert_array_equal(mesh.vertices, VERTICES)
    np.testing.assert_array_equal(mesh.faces, FACES)
    np.testing.assert_array_equal(
        mesh.colors, COLORS if colors is not None else np.empty((0, 3))
    )
    if vids is None:
        assert mesh.vids.size == 0
    else:
        np.testing.assert_array_equal(mesh.vids.ravel(), vids)


def test_drc_exact_meshing_output(tmp_path):
    pytest.importorskip("DracoPy")
    filename = str(tmp_path / "mesh.drc")
    mesh = meshing(sphere_grid())
    mesh.to_drc(filename, quantization_bits=0, preserve_order=True)
    decoded = Mesh.from_drc(filename)
    np.testing.assert_array_equal(decoded.vertices, mesh.vertices)
    np.testing.assert_array_equal(decoded.faces, mesh.faces)


def test_drc_default_keeps_vids_on_their_vertices(tmp_path):
    pytest.importorskip("DracoPy")
    filename = str(tmp_path / "mesh.drc")
    source = meshing(sphere_grid())
    vids = np.arange(len(source.vertices))
    mesh = Mesh.from_pymesh(source.vertices, source.faces, vids=vids)
    mesh.to_drc(filename)
    decoded = Mesh.from_drc(filename)

    assert len(decoded.faces) == len(mesh.faces)
    # vertices can be reordered: compare each one with the vertex its vid names
    error = decoded.vertices - mesh.vertices[decoded.vids.ravel().astype(int)]
    span = np.ptp(mesh.vertices, axis=0).max()
    assert np.abs(error).max() <= span / 2**14


def test_drc_rejects_vids_out_of_uint32(tmp_path):
    pytest.importorskip("DracoPy")
    mesh = Mesh.from_pymesh(VERTICES, FACES, vids=np.array([-1, 0, 1, 2]))
    with pytest.raises(ValueError):
        mesh.to_drc(str(tmp_path / "mesh.drc"))


@pytest.mark.parametrize(
    "duplicate",
    [copy.copy, copy.deepcopy, lambda mesh: pickle.loads(pickle.dumps(mesh))],
)
def test_copy_and_pickle(duplicate):
    mesh = duplicate(Mesh.from_pymesh(VERTICES, FACES, colors=COLORS))
    np.testing.assert_array_equal(mesh.vertices, VERTICES)
    np.testing.assert_array_equal(mesh.faces, FACES)
    np.testing.assert_array_equal(mesh.colors, COLORS)


def test_missing_attribute():
    with pytest.raises(AttributeError):
        _ = Mesh().not_a_vtk_method


def test_voxelization_scalar_size():
    grid = voxelization(meshing(sphere_grid()), voxels_size=4)
    assert np.isscalar(grid.voxels_size)
    assert grid.volume() > 0
    # 4 mm grid: consecutive positions are 4 apart along each axis
    for axis in range(3):
        steps = np.diff(np.unique(grid.voxels_position[:, axis]))
        np.testing.assert_allclose(steps, 4)


def test_voxelization_rejects_anisotropic_size():
    with pytest.raises(ValueError):
        voxelization(meshing(sphere_grid()), voxels_size=(2, 4, 8))


def test_image_from_vtk_scalar_size_round_trip(tmp_path):
    image = Image3D(np.ones((2, 2, 2)), voxels_size=2.5, world_coordinate=(1, 2, 3))
    from_vtk = Image3D.from_vtk_image(image.vtk_image_data)
    assert from_vtk.voxels_size == 2.5

    filename = str(tmp_path / "image.npz")
    from_vtk.write_to_npz(filename)
    assert Image3D.read_from_npz(filename).voxels_size == 2.5


def test_image_anisotropic_round_trip(tmp_path):
    image = Image3D(np.ones((2, 2, 2)), voxels_size=(1.0, 2.0, 3.0))
    from_vtk = Image3D.from_vtk_image(image.vtk_image_data)
    assert from_vtk.voxels_size == (1.0, 2.0, 3.0)

    filename = str(tmp_path / "image.npz")
    from_vtk.write_to_npz(filename)
    assert Image3D.read_from_npz(filename).voxels_size == (1.0, 2.0, 3.0)

    with pytest.raises(ValueError):
        VoxelGrid.from_image_3d(from_vtk)
