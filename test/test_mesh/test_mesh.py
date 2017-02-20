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
    voxels_position_to_image_3d)

from alinea.phenomenal.mesh.algorithms import meshing
from alinea.phenomenal.data_access.plant_1 import plant_1_voxel_centers
# ==============================================================================


def test_mesh_empty_voxel_centers():

    voxels_size = 8
    voxels_position = list()
    try:
        image_3d = voxels_position_to_image_3d(voxels_position, voxels_size)

    except Exception, e:
        assert type(e) == ValueError
    else:
        assert False


def test_mesh_one_voxel_centers():
    voxels_size = 1
    voxels_position = list()
    voxels_position.append((0, 0, 0))

    try:
        image_3d = voxels_position_to_image_3d(voxels_position, voxels_size)
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
    voxels_position = plant_1_voxel_centers(voxel_size=voxels_size)

    image_3d = voxels_position_to_image_3d(voxels_position, voxels_size)

    vertices, faces = meshing(image_3d,
                              smoothing_iteration=2,
                              reduction=0.95,
                              verbose=True)

    assert 100 <= len(vertices) <= 273
    assert 200 <= len(faces) <= 542

if __name__ == "__main__":
    test_mesh_empty_voxel_centers()
    test_mesh_one_voxel_centers()
    test_mesh_two_voxel_center()
    test_mesh_normal()
