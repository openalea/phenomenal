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

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.mesh as phm_mesh
from openalea.phenomenal.mesh import (
    voxel_grid_to_vtk_poly_data,
    from_voxel_centers_to_vtk_image_data,
)


# ==============================================================================


def test_mesh_error_1():
    voxels_size = 8
    voxels_position = list()
    try:
        _ = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()

    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_mesh_error_2():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))

    try:
        image_3d = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()
        _, _ = phm_mesh.meshing(image_3d)

    except Exception as e:
        assert isinstance(e, ValueError)
    else:
        assert False


def test_meshing():
    plant_number = 1
    voxels_size = 16

    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data")
    print(dir_path)
    voxel_grid = phm_data.voxel_grid(
        dir_path, plant_number=plant_number, voxels_size=voxels_size
    )

    image_3d = voxel_grid.to_image_3d()

    vertices, faces = phm_mesh.meshing(
        image_3d, smoothing_iteration=2, reduction=0.95, verbose=True
    )
    assert 100 <= len(vertices) <= 500, len(vertices)
    assert 200 <= len(faces) <= 1000, len(faces)

    poly_data = phm_mesh.from_vertices_faces_to_vtk_poly_data(vertices, faces)
    poly_data2 = voxel_grid_to_vtk_poly_data(voxel_grid)
    assert (0.05 * poly_data2.GetNumberOfVerts()) == poly_data.GetNumberOfVerts()

    vtk_image_data = phm_mesh.voxelization(poly_data, voxels_size=voxels_size)
    voxels_position = phm_mesh.from_vtk_image_data_to_voxels_center(vtk_image_data)
    image_data, (_, _, _) = from_voxel_centers_to_vtk_image_data(
        voxels_position, voxels_size
    )

    assert len(voxels_position) >= 1000


def test_format():
    vertices = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]

    faces = [[0, 1, 2]]

    filename = "test.ply"

    phm_mesh.write_vertices_faces_to_ply_file(filename, vertices, faces)

    vertices, faces, color = phm_mesh.read_ply_to_vertices_faces(filename)

    os.remove(filename)

    print(type(color))
