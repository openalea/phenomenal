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

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d_octree)

# ==============================================================================


def test_working():
    # Load images binarize
    images = plant_1_images_binarize()
    calibration = plant_1_calibration_camera_side()

    images_and_projections = list()
    for angle in range(0, 360, 30):
        img = images[angle]
        function = calibration.get_projection(angle)

        images_and_projections.append((img, function))

    voxels_size = 64
    # Multi-view reconstruction
    voxel_octree = reconstruction_3d_octree(
        images_and_projections, voxels_size=voxels_size, verbose=True)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()