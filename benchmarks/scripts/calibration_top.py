# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import cv2

from alinea.phenomenal.multi_view_reconstruction import (
    reconstruction_3d)

from alinea.phenomenal.chessboard import (
    Chessboard)

from alinea.phenomenal.calibration_opencv import (
    Calibration,
    get_function_projection)

from alinea.phenomenal.plant_1 import (
    plant_1_chessboards_path,
    plant_1_images_binarize)

from alinea.phenomenal.viewer import (
    show_points_3d)
# ==============================================================================

# Read image in BGR
im = cv2.imread('chess_top.png', cv2.IMREAD_COLOR)
height, length, _ = im.shape
print height, length


chessTop = Chessboard(47, (8, 6))
chessTop.corners_points[-1] = chessTop.find_corners_with_bgr(im, [0, 0, 255])

chessSide = Chessboard.read(plant_1_chessboards_path()[0])

cpTop = Calibration.calibrate(chessTop, (height, length))
cpSide = Calibration.calibrate(chessSide, (2454, 2056))

projectionTop = get_function_projection(cpTop, -1)
projection0 = get_function_projection(cpSide, 0)
projection90 = get_function_projection(cpSide, 90)

images = plant_1_images_binarize()
images_and_projections = list()
images_and_projections.append((images[-1], projectionTop))
images_and_projections.append((images[0], projection0))
images_and_projections.append((images[90], projection90))

voxel_size = 16
voxel_centers = reconstruction_3d(images_and_projections,
                                  voxel_size=voxel_size,
                                  verbose=True)

show_points_3d(voxel_centers)
