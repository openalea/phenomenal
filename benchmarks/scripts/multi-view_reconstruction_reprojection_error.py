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
from alinea.phenomenal.plant_1 import (
    plant_1_images_binarize,
    plant_1_calibration_camera_side_2_target)

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d,
    error_reconstruction,
    error_reconstruction_lost,
    error_reconstruction_precision)

# ==============================================================================
# LOAD DATA
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side_2_target()

# ==============================================================================
# BUILD 3D PLANT
images_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    projection = calibration.get_projection(angle)
    images_projections.append((img, projection))

voxel_size = 10
voxel_centers = reconstruction_3d(
    images_projections, voxel_size=voxel_size, verbose=True)

# ==============================================================================
# Compute error

for angle in range(0, 360, 30):
    err_lost = error_reconstruction_lost(
        images[angle],
        calibration.get_projection(angle),
        voxel_centers,
        voxel_size)

    err_precision = error_reconstruction_precision(
        images[angle],
        calibration.get_projection(angle),
        voxel_centers,
        voxel_size)

    err_reconstruction = error_reconstruction(
        images[angle],
        calibration.get_projection(angle),
        voxel_centers,
        voxel_size)

    print 'Error lost : ', err_lost
    print 'Error precision : ', err_precision
    # err_lost + err_precision = err_precision
    print 'Error reconstruction : ', err_precision,
    print err_reconstruction

