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
from __future__ import division, print_function

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.mesh as phm_mesh
# ==============================================================================


def test_mesh_error_1():

    voxels_size = 8
    voxels_position = list()
    try:
        image_3d = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()

    except Exception as e:
        assert type(e) == ValueError
    else:
        assert False


def test_mesh_error_2():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))

    try:
        image_3d = phm_obj.VoxelGrid(voxels_position, voxels_size).to_image_3d()
        vertices, faces = phm_mesh.meshing(image_3d)

    except Exception as e:
        assert type(e) == ValueError
    else:
        assert False


def test_meshing():

    plant_number = 1
    voxels_size = 16
    voxel_grid = phm_data.voxel_grid(plant_number=plant_number,
                                     voxels_size=voxels_size)

    image_3d = voxel_grid.to_image_3d()

    vertices, faces = phm_mesh.meshing(image_3d,
                                       smoothing_iteration=2,
                                       reduction=0.95,
                                       verbose=True)
    assert 100 <= len(vertices) <= 500, len(vertices)
    assert 200 <= len(faces) <= 1000, len(faces)

    poly_data = phm_mesh.from_vertices_faces_to_vtk_poly_data(vertices, faces)

    vtk_image_data = phm_mesh.voxelization(poly_data, voxels_size=voxels_size)
    voxels_position = phm_mesh.from_vtk_image_data_to_voxels_center(
        vtk_image_data)

    assert len(voxels_position) >= 1000


def test_format():
    vertices, faces, color = phm_data.synthetic_plant(plant_number=1)

    print(type(color))

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name).upper())
            eval(func_name)()
