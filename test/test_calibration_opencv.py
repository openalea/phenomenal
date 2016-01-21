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
import numpy
import os

from alinea.phenomenal.multi_view_reconstruction import reconstruction_3d
from alinea.phenomenal.chessboard import Chessboard
from alinea.phenomenal.plant_1 import (plant_1_chessboards_path,
                                       plant_1_images_binarize)
from alinea.phenomenal.calibration_opencv import (CameraParameters,
                                                  Calibration,
                                                  Projection)
# ==============================================================================


def test_calibration_opencv():
    chessboards_path = plant_1_chessboards_path()

    # Load Chessboard
    chessboard_1 = Chessboard.read(chessboards_path[0])

    c = Calibration()
    cp = c.calibrate(chessboard_1, (2056, 2454))
    cp.write('test_calibration_opencv')
    cp = CameraParameters.read('test_calibration_opencv')

    p = Projection(cp)

    images_binarize = plant_1_images_binarize()
    images_selected = dict()
    for angle in [0, 30, 60, 90]:
        images_selected[angle] = images_binarize[angle]

    points = reconstruction_3d(images_selected, p, 8, verbose=True)

    assert len(points) == 11054

    os.remove('test_calibration_opencv.json')

def test_camera_opencv_parameters():
    cp = CameraParameters()

    assert (cp.focal_matrix == 0).all()
    assert (cp.distortion_coefficient == 0).all()
    assert cp.rotation_vectors == dict()
    assert cp.translation_vectors == dict()

    cp.focal_matrix[0][0] = 42
    cp.focal_matrix[1][1] = 1
    cp.focal_matrix[2][2] = 7

    cp.distortion_coefficient[0][0] = 1
    cp.distortion_coefficient[1][0] = 2
    cp.distortion_coefficient[2][0] = 3
    cp.distortion_coefficient[3][0] = 4
    cp.distortion_coefficient[4][0] = 5

    cp.rotation_vectors[42] = numpy.zeros((3, 1))
    cp.rotation_vectors[0] = numpy.ones((3, 1))

    cp.translation_vectors[10] = numpy.ones((3, 1))
    cp.translation_vectors[80] = numpy.zeros((3, 1))

    cp.write('test_camera_opencv_parameters')
    new_cp = CameraParameters.read('test_camera_opencv_parameters')

    assert new_cp.focal_matrix[0][0] == 42
    assert new_cp.focal_matrix[1][1] == 1
    assert new_cp.focal_matrix[2][2] == 7

    assert new_cp.distortion_coefficient[0][0] == 1
    assert new_cp.distortion_coefficient[1][0] == 2
    assert new_cp.distortion_coefficient[2][0] == 3
    assert new_cp.distortion_coefficient[3][0] == 4
    assert new_cp.distortion_coefficient[4][0] == 5

    assert (new_cp.rotation_vectors[42] == 0).all()
    assert (new_cp.rotation_vectors[0] == 1).all()

    assert (new_cp.translation_vectors[10] == 1).all()
    assert (new_cp.translation_vectors[80] == 0).all()

    os.remove('test_camera_opencv_parameters.json')

if __name__ == "__main__":
    test_camera_opencv_parameters()
    test_calibration_opencv()
