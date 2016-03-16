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
    volume)

import alinea.phenomenal.viewer
import alinea.phenomenal.misc
# ==============================================================================

# Load images binarize
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side_2_target()


# Select images
images_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    projection = calibration.get_projection(angle)
    images_projections.append((img, projection))

voxel_size = 10
# Multi-view reconstruction
voxel_centers = reconstruction_3d(
    images_projections, voxel_size=voxel_size, verbose=True)

print len(voxel_centers)

# # Write
# alinea.phenomenal.misc.write_xyz(voxel_centers,
#                                  'voxel_centers_size_' + str(voxel_size))

# # Read
# points_3d = alinea.phenomenal.misc.read_xyz('points_3d_radius_' + str(radius))

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=10)

