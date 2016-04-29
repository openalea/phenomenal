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
import time

import alinea.phenomenal.calibration
import alinea.phenomenal.misc
import alinea.phenomenal.viewer
from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d)

from alinea.phenomenal.plant_1 import (
    plant_1_images_binarize,
    plant_1_calibration_camera_side_2_target)
# ==============================================================================

# Load images binarize
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side_2_target()

calibration_side = alinea.phenomenal.calibration.CalibrationCamera.load(
    "chessboard_2013-07-11_15-49-42_vis_wide_side_calibration")

calibration_top = alinea.phenomenal.calibration.CalibrationCamera.load(
    "chessboard_2013-07-11_15-49-42_vis_wide_top_calibration")


# Select images
images_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    projection = calibration_side.get_projection(angle)
    images_projections.append((img, projection))

img = images[-1]
projection = calibration_top.get_projection(0)
images_projections.append((img, projection))


voxel_size = 4

t0 = time.time()
# Multi-view reconstruction
voxel_centers = reconstruction_3d(
    images_projections, voxel_size=voxel_size, verbose=True)

print "Time to reconstruct plant : ", time.time() - t0
print len(voxel_centers)

# # Write
# alinea.phenomenal.misc.write_xyz(voxel_centers,
#                                  'voxel_centers_size_' + str(voxel_size))
#
# # Read
# points_3d = alinea.phenomenal.misc.read_xyz(
#     'voxel_centers_size_' + str(voxel_size))

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers,
                                        scale_factor=voxel_size,
                                        color=(0.1, 0.8, 0.1),
                                        figure_name=str(voxel_size))
