# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os
import numpy as np

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.mesh as phm_mesh

from pathlib import Path
test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir.parent / "data" / "plant_1"
# ==============================================================================


def test_mesh_error_1():
    voxels_size = 8
    voxels_position = list()
    voxel_grid = phm_obj.VoxelGrid(voxels_position, voxels_size)
    try:
        _ = phm_mesh.meshing(voxel_grid)

    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_mesh_error_2():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))
    voxel_grid = phm_obj.VoxelGrid(voxels_position, voxels_size)

    try:
        _ = phm_mesh.meshing(voxel_grid)

    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_meshing():

    voxels_size = 16


    voxel_grid = phm_data.voxel_grid(
        data_dir, voxels_size=voxels_size
    )

    mesh = phm_mesh.meshing(
        voxel_grid, smoothing_iteration=2, reduction=0.95, verbose=True
    )
    n_vertices = len(mesh.vertices)
    n_faces = len(mesh.faces)
    assert 100 <= n_vertices <= 500, n_vertices
    assert 200 <= n_faces <= 1000, n_faces

    bbox_min, bbox_max = voxel_grid.bounding_box()

    bounds = mesh.poly_data.GetBounds()
    mesh_min = np.array(bounds[::2])
    mesh_max = np.array(bounds[1::2])

    np.testing.assert_allclose(
        mesh_min, bbox_min, atol=voxels_size,
        err_msg="Mesh minimum bounds differ from voxel grid",
    )
    np.testing.assert_allclose(
        mesh_max, bbox_max, atol=voxels_size,
        err_msg="Mesh maximum bounds differ from voxel grid",
    )



    poly_data2 = voxel_grid.to_vtk_poly_data()
    assert (0.05 * poly_data2.GetNumberOfVerts()) == mesh.poly_data.GetNumberOfVerts()

    voxel_grid2 = phm_mesh.voxelization(mesh, voxels_size=voxels_size)


    assert len(voxel_grid2.voxels_position) >= 1000


def test_format():
    vertices = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]

    faces = [[0, 1, 2]]

    mesh = phm_obj.Mesh.from_pymesh(vertices, faces)

    filename = "test.ply"

    mesh.write_ply(filename)

    rmesh = phm_obj.Mesh.from_ply(filename)

    assert len(rmesh.vertices) == len(mesh.vertices)
    os.remove(filename)
