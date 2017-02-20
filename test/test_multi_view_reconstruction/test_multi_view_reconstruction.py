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
from alinea.phenomenal.data_access.plant_1 import (
    plant_1_calibration_camera_side,
    plant_1_images_binarize)

from alinea.phenomenal.multi_view_reconstruction.multi_view_reconstruction \
    import (reconstruction_3d)

# ==============================================================================


def test_multi_view_reconstruction_reconstruction_3d():

    # Load images binarize
    images = plant_1_images_binarize()
    calibration = plant_1_calibration_camera_side()

    images_and_projections = list()
    for angle in range(0, 360, 30):
        img = images[angle]
        function = calibration.get_projection(angle)

        images_and_projections.append((img, function))

    voxel_size = 64
    # Multi-view reconstruction
    voxel_centers = reconstruction_3d(images_and_projections,
                                      voxel_size=voxel_size,
                                      verbose=True)

    assert len(voxel_centers) == 437

if __name__ == "__main__":
    test_multi_view_reconstruction_reconstruction_3d()
