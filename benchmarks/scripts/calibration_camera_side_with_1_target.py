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
    plant_1_chessboards,
    plant_1_images_binarize)

import alinea.phenomenal.chessboard
from alinea.phenomenal.calibration import (
    CalibrationCameraSideWith1Target)

import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
# ==============================================================================
# Load Chessboard
chess_1, _, _ = plant_1_chessboards()

# ==============================================================================
# Calibration

calibration = alinea.phenomenal.calibration.CalibrationCameraSideWith1Target()
calibration.calibrate(chess_1.get_corners_2d(),
                      chess_1.get_corners_local_3d(),
                      (2056, 2454),
                      number_of_repetition=3,
                      verbose=True)

# Dump & Load
calibration.dump('benchmarks_calibration_1_target')
calibration = CalibrationCameraSideWith1Target.load(
    'benchmarks_calibration_1_target')

# ==============================================================================

images = alinea.phenomenal.plant_1.plant_1_images_binarize()
images_and_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    function = calibration.get_projection(angle)
    images_and_projections.append((img, function))

voxel_size = 10
# Multi-view reconstruction
voxel_centers = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_and_projections, voxel_size=voxel_size, verbose=True)

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=10)

# ==============================================================================

import alinea.phenomenal.viewer
import cv2
import glob

data_directory = '../../local/CHESSBOARD_1/'
files_path = glob.glob(data_directory + '*.png')
angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_path)

for i in range(len(files_path)):
    angle = angles[i]
    if angle in [0, 90]:
        img = cv2.imread(files_path[i], cv2.IMREAD_UNCHANGED)

        points_2d = calibration.get_target_projected(
            angles[i], chess_1.get_corners_local_3d())

        # Blue is pt ref
        # Red is pt projected
        alinea.phenomenal.viewer.show_chessboard_3d_projection_on_image(
            img,
            chess_1.corners_points[angle],
            points_2d,
            name_windows=str(angles[i]))
