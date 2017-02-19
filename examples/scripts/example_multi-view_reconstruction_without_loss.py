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
from alinea.phenomenal.display import (
    show_voxels)

from alinea.phenomenal.multi_view_reconstruction\
    .multi_view_reconstruction_without_loss import (reconstruction_without_loss)

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_images_binarize,
    plant_1_calibration_camera_side,
    plant_1_calibration_camera_top)

# ==============================================================================


if __name__ == '__main__':

    images = plant_1_images_binarize()

    calibration_side = plant_1_calibration_camera_side()
    calibration_top = plant_1_calibration_camera_top()

    # Select images
    refs_angle_list = [120]
    images_projections_refs = list()
    for angle in range(0, 360, 30):
        ref = False
        if angle in refs_angle_list:
            ref = True

        img = images[angle]
        projection = calibration_side.get_projection(angle)
        images_projections_refs.append((img, projection, ref))

    img = images[-1]
    projection = calibration_top.get_projection(0)
    images_projections_refs.append((img, projection, False))

    voxels_size = 4
    error_tolerance = 0
    voxels_position = reconstruction_without_loss(
        images_projections_refs,
        voxel_size=voxels_size,
        error_tolerance=error_tolerance,
        verbose=True)

    print("Number of voxel : {number_voxel}".format(
        number_voxel=len(voxels_position)))

    # Viewing
    show_voxels(voxels_position, voxels_size,
                size=(5000, 5000),
                color=(0.1, 0.9, 0.1),
                azimuth=310,
                distance=3000,
                elevation=90,
                focalpoint=(0, 0, 0))
