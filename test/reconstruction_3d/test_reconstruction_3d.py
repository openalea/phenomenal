# -*- python -*-
#
#       test_octree: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 
import cv2
import glob
import random
import numpy as np

#       =======================================================================
#       Local Import 

import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard

from phenomenal.test import tools_test

#       =======================================================================


def test_reconstruction_3d():

    #   =======================================================================

    my_calibration = calibration_chessboard.Calibration.read_calibration(
        '../calibration/calibration')

    directory = '../../local/data/tests/Samples_binarization_2/'
    # directory = '../../local/data/tests/Samples_binarization_4/'
    # directory = '../../local/data/tests/Samples_binarization_5/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        if (angles[i] is not 120 or angles[i] is not 150 or
                angles[i] is not 300 or angles[i] is not 330):
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)

    octree_result = reconstruction_3d.reconstruction_3d(
        images, my_calibration, 5)

    tools_test.show_cube(octree_result, 9, "OpenCv")

    reconstruction_3d.reprojection_3d_objects_to_images(
        images, octree_result, my_calibration)


def test_new_reconstruction_3d():

    #   =======================================================================

    my_calibration = calibration_chessboard.Calibration.read_calibration(
        '../calibration/calibration')

    directory = '../../local/data/tests/Samples_binarization_2/'
    # directory = '../../local/data/tests/Samples_binarization_4/'
    # directory = '../../local/data/tests/Samples_binarization_5/'
    # directory = '../../local/data/tests/Samples_binarization_2/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        if angles[i] < 210:
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)

    octree_result = reconstruction_3d.new_reconstruction_3d(
        images, my_calibration, 10)

    tools_test.show_cube(octree_result, 9, "OpenCv")

    reconstruction_3d.reprojection_3d_objects_to_images(
        images, octree_result, my_calibration)


def select_random_image(number_of_image, angles, images):
    tmp_angles = list(angles)

    tmp_angles.remove(330)
    tmp_angles.remove(300)

    selected_images = dict()

    for i in range(number_of_image):
        angle = random.choice(tmp_angles)
        tmp_angles.remove(angle)
        selected_images[angle] = images[angle]

    return selected_images


def create_matrix(cubes):
    matrix = np.zeros((5000, 5000, 5000))

    for cube in cubes:
        x = cube.center.x
        y = cube.center.y
        z = cube.center.z
        r = cube.radius

        matrix[
        x - r: x + r,
        y - r: y + r,
        z - r: z + r] = 1


def test_matrix():
    my_calibration = calibration_chessboard.Calibration.read_calibration(
        '../calibration/calibration')

    directory = '../../local/data/tests/Samples_binarization_2/'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    octree_result = reconstruction_3d.reconstruction_3d(
            images, my_calibration, 10)

    tools_test.show_cube(octree_result, 9, "OpenCv")

    create_matrix(octree_result)


def test_bootstrap():
    my_calibration = calibration_chessboard.Calibration.read_calibration(
        '../calibration/calibration')

    directory = '../../local/data/tests/Samples_binarization_2/'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    results_reconstruction_3d = list()

    for i in range(10):
        selected_images = select_random_image(5, angles, images)

        octree_result = reconstruction_3d.reconstruction_3d(
            selected_images, my_calibration, 10)

        results_reconstruction_3d.append(octree_result)

    tools_test.show_cube(octree_result, 9, "OpenCv")


    # reconstruction_3d.reprojection_3d_objects_to_images(
    #     images, octree_result, my_calibration)


if __name__ == "__main__":
    test_reconstruction_3d()
    # test_new_reconstruction_3d()
    # test_bootstrap()
    # test_matrix()