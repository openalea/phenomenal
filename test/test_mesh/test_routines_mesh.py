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
import openalea.phenomenal.data as phm_data
import openalea.phenomenal.mesh as phm_mesh


from pathlib import Path
HERE = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
DATADIR = HERE.parent / "data" / "plant_1"
# ==============================================================================


def test_normals_centers():

    voxels_size = 16

    voxel_grid = phm_data.voxel_grid(
        DATADIR, voxels_size=voxels_size
    )

    image_3d = voxel_grid.to_image_3d()

    vertices, faces = phm_mesh.meshing(
        image_3d, smoothing_iteration=2, reduction=0.95, verbose=True
    )
    normals = phm_mesh.normals(vertices, faces)
    centers = phm_mesh.centers(vertices, faces)

    assert len(normals) == len(faces)
    assert len(centers) == len(faces)
