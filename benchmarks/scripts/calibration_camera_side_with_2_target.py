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
import alinea.phenomenal.plant_1
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
from alinea.phenomenal.chessboard import (
    Chessboard)
from alinea.phenomenal.calibration import (
    CalibrationCameraSideWith2Target)
# ==============================================================================

chessboards_path = alinea.phenomenal.plant_1.plant_1_chessboards_path()

# Load Chessboard
chessboard_1 = Chessboard.load(chessboards_path[0])
chessboard_2 = Chessboard.load(chessboards_path[1])

size_image = (2056, 2454)
calibration_side = CalibrationCameraSideWith2Target()
calibration_side.calibrate(chessboard_1.get_corners_2d(),
                           chessboard_1.get_corners_local_3d(),
                           chessboard_2.get_corners_2d(),
                           chessboard_2.get_corners_local_3d(),
                           size_image,
                           number_of_repetition=3,
                           verbose=True)

calibration_side.dump('calibration_camera_side_2_target')
calibration_side = CalibrationCameraSideWith2Target.load(
    'calibration_camera_side_2_target')


# ==============================================================================


images = alinea.phenomenal.plant_1.plant_1_images_binarize()
images_and_projections = list()
for angle in range(0, 360, 30):
    img = images[angle]
    function = calibration_side.get_projection(angle)
    images_and_projections.append((img, function))

voxel_size = 5
# Multi-view reconstruction
voxel_centers = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_and_projections, voxel_size=voxel_size, verbose=True)

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=10)
