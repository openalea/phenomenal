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
import numpy
import cv2

import alinea.phenomenal.plant_1
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
from alinea.phenomenal.chessboard import (
    Chessboard)
from alinea.phenomenal.calibration import (
    CalibrationCamera,
    CalibrationCameraTopWith1Target,
    CalibrationCameraSideWith1Target)


# ==============================================================================

# chessboards_path = alinea.phenomenal.plant_1.plant_1_chessboards_path()
#
# # Load Chessboard
# chessboard_1 = Chessboard.load(chessboards_path[0])
# chessboard_2 = Chessboard.load(chessboards_path[1])
#
# size_image = (2056, 2454)
# calibration_side = CalibrationCameraSideWith1Target()
# calibration_side.calibrate(chessboard_1.get_corners_2d(),
#                            chessboard_1.get_corners_local_3d(),
#                            size_image,
#                            number_of_repetition=3,
#                            verbose=True)
#
# calibration_side.dump('calibration_side')
calibration_side = CalibrationCameraSideWith1Target.load('calibration_side')


# ==============================================================================

# Read image in BGR
im = cv2.imread('chess_top.png', cv2.IMREAD_COLOR)

corner_top = [[[1270, 1432]],
              [[1320, 1372]],
              [[1371, 1314]],
              [[1421, 1254]],
              [[1472, 1194]],
              [[1522, 1135]],
              [[1573, 1075]],
              [[1623, 1016]],

              [[1282, 1438]],
              [[1332, 1380]],
              [[1381, 1322]],
              [[1431, 1263]],
              [[1480, 1205]],
              [[1530, 1147]],
              [[1579, 1089]],
              [[1628, 1030]],

              [[1294, 1445]],
              [[1342, 1387]],
              [[1391, 1330]],
              [[1439, 1272]],
              [[1487, 1216]],
              [[1536, 1158]],
              [[1584, 1101]],
              [[1633, 1045]],

              [[1305, 1450]],
              [[1352, 1393]],
              [[1400, 1337]],
              [[1447, 1281]],
              [[1495, 1225]],
              [[1543, 1169]],
              [[1590, 1113]],
              [[1637, 1056]],

              [[1315, 1455]],
              [[1362, 1400]],
              [[1409, 1345]],
              [[1455, 1290]],
              [[1502, 1235]],
              [[1549, 1179]],
              [[1595, 1124]],
              [[1641, 1070]],

              [[1326, 1461]],
              [[1372, 1407]],
              [[1417, 1352]],
              [[1463, 1298]],
              [[1509, 1244]],
              [[1554, 1189]],
              [[1600, 1135]],
              [[1646, 1082]]]

chess_top = Chessboard(47, (8, 6))
chess_top.corners_points[0] = numpy.array(corner_top)
chess_top.dump("chessboard_top")

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
                          number_of_repetition=10,
                          verbose=True)

calibration_top.dump("calibration_top")
calibration_top = CalibrationCamera.load("calibration_top")

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

voxel_size = 10
# Multi-view reconstruction
voxel_centers = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_and_projections, voxel_size=voxel_size, verbose=True)

# Viewing
alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=10)
