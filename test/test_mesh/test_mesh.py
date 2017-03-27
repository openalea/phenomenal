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

from alinea.phenomenal.mesh import meshing
from alinea.phenomenal.data_access import plant_1_voxel_point_cloud
# ==============================================================================


def test_mesh_empty_voxel_centers():

    voxels_size = 8
    voxels_position = list()
    try:
        image_3d = VoxelPointCloud(voxels_position, voxels_size).to_image_3d()

    except Exception, e:
        assert type(e) == ValueError
    else:
        assert False


def test_mesh_one_voxel_centers():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))

    try:
        image_3d = VoxelPointCloud(voxels_position, voxels_size).to_image_3d()
        vertices, faces = meshing(image_3d)

    except Exception, e:
        assert type(e) == ValueError
    else:
        assert False


def test_mesh_two_voxel_center():
    voxels_size = 4
    voxels_position = list()
    voxels_position.append((0, 0, 0))
    voxels_position.append((4, 4, 8))
    voxels_position.append((8, 8, 8))

    # image_3d = voxels_position_to_image_3d(voxel_centers, voxel_size)
    # print image_3d.size
    # vertices, faces = meshing(image_3d)


def test_mesh_normal():
    voxels_size = 20
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)

    image_3d = vpc.to_image_3d()

    vertices, faces = meshing(image_3d,
                              smoothing_iteration=2,
                              reduction=0.95,
                              verbose=True)

    assert 100 <= len(vertices) <= 273
    assert 200 <= len(faces) <= 542

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
