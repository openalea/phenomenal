# -*- python -*-
#
#       test_reconstruction_3d_manual_calibration.py :
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
#       ========================================================================

#       ========================================================================
#       External Import
import glob
import cv2

#       ========================================================================
#       Local Import 
from phenomenal.test import tools_test
import alinea.phenomenal.calibration_manual as calibration_manual
import alinea.phenomenal.reconstruction_3d as reconstruction_3d

#       ========================================================================
#       Code


def test_reconstruction_3d_samples_binarization_1():
    #   ========================================================================
    #   Input
    images_path = ['../../local/data/tests/Samples_binarization_1/top.png',
                   '../../local/data/tests/Samples_binarization_1/side0.png',
                   '../../local/data/tests/Samples_binarization_1/side90.png']

    angles = [-1, 0, 90]

    images = dict()
    for i in range(len(images_path)):
        images[angles[i]] = cv2.imread(images_path[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================
    #   Binarize images
    for angle in images.keys():
        im = images[angle]

        im[im == 255] = 0
        im[im != 0] = 255

    #   ========================================================================
    #   Load manual configuration

    camera_configuration = calibration_manual.CameraConfiguration()
    calibration = calibration_manual.Calibration(camera_configuration)

    #   ========================================================================
    #   Reconstruction 3D

    octree_result = reconstruction_3d.reconstruction_3d_manual_calibration(
        images, calibration, 1)

    tools_test.show_cube(octree_result, 1)


def test_reconstruction_3d_samples_binarization_2():
    #   ========================================================================
    #   Input

    directory = '../../local/data/tests/Samples_binarization_6/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    camera_configuration = calibration_manual.CameraConfiguration()
    calibration = calibration_manual.Calibration(camera_configuration)

    #   ========================================================================
    #   Reconstruction 3D

    # cubes = reconstruction_3d.reconstruction_3d_manual_calibration(
    #     images, calibration, 0.5)
    #
    # tools_test.show_cube(cubes, 1)


    cubes = reconstruction_3d.reconstruction_3d_n(
        images, calibration, 0.5)

    tools_test.show_cubes(cubes, scale_factor=1)

#       ========================================================================
#       TEST

if __name__ == "__main__":
    # test_reconstruction_3d_samples_binarization_1()
    test_reconstruction_3d_samples_binarization_2()
