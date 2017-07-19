# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from alinea.phenomenal.data_structure import (
    VoxelPointCloud)

from alinea.phenomenal.mesh import (
    meshing,
    voxelization,
    from_vertices_faces_to_vtk_poly_data,
    from_vtk_image_data_to_voxels_center)

from alinea.phenomenal.data_access import plant_1_voxel_point_cloud
# ==============================================================================


def test_mesh_error_1():

    voxels_size = 8
    voxels_position = list()
    try:
        image_3d = VoxelPointCloud(voxels_position, voxels_size).to_image_3d()

    except Exception as e:
        assert type(e) == ValueError
    else:
        assert False


def test_mesh_error_2():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))

    try:
        image_3d = VoxelPointCloud(voxels_position, voxels_size).to_image_3d()
        vertices, faces = meshing(image_3d)

    except Exception as e:
        assert type(e) == ValueError
    else:
        assert False


def test_meshing():

    voxels_size = 20
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)

    image_3d = vpc.to_image_3d()

    vertices, faces = meshing(image_3d,
                              smoothing_iteration=2,
                              reduction=0.95,
                              verbose=True)

    assert 100 <= len(vertices) <= 273
    assert 200 <= len(faces) <= 542

    poly_data = from_vertices_faces_to_vtk_poly_data(vertices, faces)

    vtk_image_data = voxelization(poly_data, voxels_size=voxels_size)
    voxels_position = from_vtk_image_data_to_voxels_center(vtk_image_data)

    assert len(voxels_position) == 1416

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name).upper())
            eval(func_name)()
