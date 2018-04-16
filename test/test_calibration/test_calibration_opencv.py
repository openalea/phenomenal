# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import numpy
import os

import openalea.phenomenal.calibration as phm_calib
# ==============================================================================


def test_calibration_opencv():
    pass
    # chess_1, chess_2 = plant_1_chessboards()
    #
    # calibration = CalibrationCameraOpenCv()
    # calibration.calibrate(chess_1.image_points['side'],
    #                       chess_1.get_corners_local_3d(),
    #                       chess_2.image_points['side'],
    #                       chess_2.get_corners_local_3d(),
    #                       (2056, 2454))
    #
    # calibration.dump('test_calibration_opencv')
    # calibration = CalibrationCameraOpenCv.load('test_calibration_opencv')
    #
    # images_binarize = plant_1_images_binarize()
    # images_projections = list()
    # for angle in [0, 30, 60, 90]:
    #     img = images_binarize[angle]
    #     projection = calibration.get_projection(angle)
    #     images_projections.append((img, projection))
    #
    # voxel_size = 16
    # voxel_centers = reconstruction_3d(images_projections,
    #                                   voxel_size=voxel_size,
    #                                   verbose=True)
    #
    # assert len(voxel_centers) <= 12000
    #
    # os.remove('test_calibration_opencv.json')


def test_camera_opencv_parameters():
    cp = phm_calib.CalibrationCameraOpenCv()

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

    cp.dump('test_camera_opencv_parameters')
    new_cp = phm_calib.CalibrationCameraOpenCv.load(
        'test_camera_opencv_parameters')

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
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
