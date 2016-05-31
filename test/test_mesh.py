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
import alinea.phenomenal.data_transformation
import alinea.phenomenal.mesh
import alinea.phenomenal.plant_1
# ==============================================================================


def test_mesh_empty_voxel_centers():

    voxel_size = 8
    voxel_centers = list()

    vertices, faces = alinea.phenomenal.mesh.meshing(
        voxel_centers, voxel_size)

    assert vertices == list()
    assert faces == list()


def test_mesh_one_voxel_centers():
    voxel_size = 1
    voxel_centers = list()
    voxel_centers.append((0, 0, 0))

    vertices, faces = alinea.phenomenal.mesh.meshing(
        voxel_centers, voxel_size)

    assert vertices == list()
    assert faces == list()


def test_mesh_two_voxel_center():
    voxel_size = 4
    voxel_centers = list()
    voxel_centers.append((0, 0, 0))
    voxel_centers.append((4, 4, 8))

    vertices, faces = alinea.phenomenal.mesh.meshing(
        voxel_centers, voxel_size)


def test_mesh_normal():
    voxel_size = 20
    voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(
        voxel_size=voxel_size)

    vertices, faces = alinea.phenomenal.mesh.meshing(
        voxel_centers, voxel_size,
        smoothing_iteration=3, reduction=0.95, verbose=True)

    print len(vertices), len(faces)

    assert len(vertices) == 273
    assert len(faces) == 542

if __name__ == "__main__":
    test_mesh_empty_voxel_centers()
    test_mesh_one_voxel_centers()
    test_mesh_two_voxel_center()
    test_mesh_normal()
