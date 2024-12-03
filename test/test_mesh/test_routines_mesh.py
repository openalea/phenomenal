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
import openalea.phenomenal.mesh as phm_mesh

# ==============================================================================


def test_normals_centers():
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
    normals = phm_mesh.normals(vertices, faces)
    centers = phm_mesh.centers(vertices, faces)

    assert len(normals) == len(faces)
    assert len(centers) == len(faces)
