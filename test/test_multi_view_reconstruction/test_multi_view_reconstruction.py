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

from alinea.phenomenal.data_structure import (
    ImageView)

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d)

# ==============================================================================


def test_multi_view_reconstruction_reconstruction_3d():

    # Load images binarize
    images = plant_1_images_binarize()
    calibration = plant_1_calibration_camera_side()

    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)
        iv = ImageView(images[angle], projection, inclusive=False)
        image_views.append(iv)

    voxels_size = 64
    # Multi-view reconstruction
    voxel_centers = reconstruction_3d(image_views,
                                      voxels_size=voxels_size,
                                      verbose=True)

    assert len(voxel_centers) == 437

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
