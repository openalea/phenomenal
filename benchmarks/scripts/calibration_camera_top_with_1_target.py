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
import cv2

from alinea.phenomenal.plant_1 import (
    plant_1_chessboards)

import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer

from alinea.phenomenal.viewer import (
    show_chessboard_3d_projection_on_image)

from alinea.phenomenal.calibration import (
    CalibrationCameraTopWith1Target,
    CalibrationCameraSideWith1Target)

# ==============================================================================

calibration_side = CalibrationCameraSideWith1Target.load(
    'benchmarks_calibration_1_target')

chess_1, chess_2, chess_top = plant_1_chessboards()

# ==============================================================================

ref_target_points_global_3d = dict()
for angle in chess_top.get_corners_2d():
    ref_target_points_global_3d[angle] = \
        calibration_side.get_ref_points_global_3d(
            angle, chess_top.get_corners_local_3d())

size_image_top = (2454, 2056)

calibration_top = CalibrationCameraTopWith1Target()
calibration_top.calibrate(chess_top.get_corners_2d(),
                          ref_target_points_global_3d,
                          size_image_top,
                          calibration_side._angle_factor,
                          number_of_repetition=20,
                          verbose=True)

calibration_top.dump("benchmarks_calibration_top")
calibration_top = CalibrationCameraTopWith1Target.load(
    "benchmarks_calibration_top")

# ==============================================================================

angle = 0
points_2d = calibration_top.get_global_point_projected(
    ref_target_points_global_3d[angle])

img_top = cv2.imread('../../local/chess_top.png', cv2.IMREAD_COLOR)
show_chessboard_3d_projection_on_image(
    img_top,
    chess_top.corners_points[angle],
    points_2d,
    name_windows=str(angle))

# ==============================================================================

images = alinea.phenomenal.plant_1.plant_1_images_binarize()
images_and_projections = list()
for angle in [0, 90]:
    img = images[angle]
    function = calibration_side.get_projection(angle)
    images_and_projections.append((img, function))

img_top = images[-1]
function_top = calibration_top.get_projection(0)
images_and_projections.append((img_top, function_top))

voxel_size = 5
# Multi-view reconstruction
voxel_centers = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_and_projections, voxel_size=voxel_size, verbose=True)

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=10)
