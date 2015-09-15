# -*- python -*-
#
#       test_calibration_chessboard.py:
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
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.calibration_tools as calibration_tools
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.reconstruction_3d_algorithm as reconstruction_3d_algorithm
import alinea.phenomenal.configuration as configuration
import alinea.phenomenal.binarization as binarization

from phenomenal.test import tools_test

#       ========================================================================
#       Code


def get_parameters():
    directory = '../../local/data/CHESSBOARD/'
    files_sv = glob.glob(directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()

    files_tv = glob.glob(directory + '*tv*.png')
    images[-1] = cv2.imread(files_tv[0], cv2.IMREAD_COLOR)

    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_GRAYSCALE)

    chessboard = calibration_chessboard.Chessboard(47, 8, 6)

    return images, chessboard


def test_calibration():
    images, chessboard = get_parameters()

    my_calibration = calibration_chessboard.calibration(
        images, chessboard)

    my_calibration.print_value()

    calibration_tools.plot_vectors(my_calibration.rotation_vectors)
    calibration_tools.plot_vectors(my_calibration.translation_vectors)

    my_calibration.write_calibration('calibration')


def get_parameters_2():
    directory = '../../local/data/CHESSBOARD_2/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    chessboard = calibration_chessboard.Chessboard(47, 8, 6)

    return images, chessboard


def test_calibration_2():
    images, chessboard = get_parameters_2()

    my_calibration = calibration_chessboard.calibration(images, chessboard)

    my_calibration.print_value()
    calibration_tools.plot_vectors(my_calibration.rotation_vectors)
    calibration_tools.plot_vectors(my_calibration.translation_vectors)

    my_calibration.write_calibration('my_calibration')


def test_re_projection():
    images, chessboard = get_parameters_2()

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'my_calibration')

    opencv_calibration.print_value()

    object_points = chessboard.object_points
    focal_matrix = opencv_calibration.focal_matrix
    distortion_coefficient = opencv_calibration.distortion_coefficient

    for angle in images:
        if angle % 30 == 0:

            rotation_vector = opencv_calibration.rotation_vectors[angle]
            translation_vector = opencv_calibration.translation_vectors[angle]

            projection_point, _ = cv2.projectPoints(object_points,
                                                    rotation_vector,
                                                    translation_vector,
                                                    focal_matrix,
                                                    distortion_coefficient)

            img = images[angle]
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            projection_point = projection_point.astype(int)
            img[projection_point[:, 0, 0],
                projection_point[:, 0, 1]] = [0, 0, 255]

            tools_test.show_image(img)


def test_compute_rotation_and_translation_vectors():
    my_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    my_calibration.print_value()

    angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]

    calibration_tools.compute_rotation_vectors(
        my_calibration.rotation_vectors, angles)
    my_calibration.write_calibration('calibration')
    calibration_tools.plot_vectors(my_calibration.rotation_vectors)

    calibration_tools.compute_translation_vectors(
        my_calibration.translation_vectors, angles)
    my_calibration.write_calibration('calibration')
    calibration_tools.plot_vectors(my_calibration.translation_vectors)


def test_calibration_on_reconstruction_3d():

    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'my_calibration')

    opencv_calibration.print_value()
    calibration_tools.plot_vectors(opencv_calibration.rotation_vectors)
    calibration_tools.plot_vectors(opencv_calibration.translation_vectors)

    image_0_90 = dict()
    image_180_270 = dict()
    image_0_270 = dict()

    for angle in images:
        if angle <= 105:
            image_0_90[angle] = images[angle]

        if 180 <= angle <= 270:
            image_180_270[angle] = images[angle]

            # opencv_calibration.rotation_vectors[angle] = \
            #     opencv_calibration.rotation_vectors[angle - 180]
            #
            # opencv_calibration.translation_vectors[angle] = \
            #     opencv_calibration.translation_vectors[angle - 180]

        if 0 <= angle <= 90 or 180 <= angle <= 270:
            image_0_270[angle] = images[angle]

    opencv_calibration.print_value()

    opencv_cubes_1 = reconstruction_3d.reconstruction_3d(
        image_0_90, opencv_calibration, 10)

    tools_test.show_cube(opencv_cubes_1, 10, "0 - 90")

    opencv_cubes_2 = reconstruction_3d.reconstruction_3d(
        image_180_270, opencv_calibration, 10)

    tools_test.show_cube(opencv_cubes_2, 10, "180 - 270")

    opencv_cubes_3 = reconstruction_3d.reconstruction_3d(
        image_0_270, opencv_calibration, 10)

    tools_test.show_cube(opencv_cubes_3, 10, "0 - 270")

    opencv_cubes_1 += opencv_cubes_2

    tools_test.show_cube(opencv_cubes_1, 10, "2")

    f = open('reconstruction_3d.xyz', 'w')

    for cube in opencv_cubes_1:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f \n" % (x, y, z))

    f.close()

    # def is_in_cubes(cubes, cube):
    #     for tmp_cube in cubes:
    #         if tmp_cube.position[0, 0] == cube.position[0, 0]:
    #             if tmp_cube.position[0, 1] == cube.position[0, 1]:
    #                 if tmp_cube.position[0, 2] == cube.position[0, 2]:
    #                     return True
    #     return False
    #
    # cubes = list()
    # for cube_1 in opencv_cubes_1:
    #     if is_in_cubes(opencv_cubes_2, cube_1):
    #         cubes.append(cube_1)
    #
    # tools_test.show_cube(cubes, 10, "OpenCv")

    #   ========================================================================

    # octree = reconstruction_3d.new_reconstruction_3d(
    #     images, opencv_calibration, 1)
    #
    # tools_test.show_octree(octree, 1, "Octree")
    #

    #   ========================================================================
    #
    # manual_calibration = calibration_manual.CameraConfiguration()
    # manual_calibration = calibration_manual.Calibration(manual_calibration)
    #
    # manual_cubes = reconstruction_3d.reconstruction_3d_manual_calibration(
    #     images, manual_calibration, 0.5)
    #
    # tools_test.show_cube(manual_cubes, 1, "Manual")

    #   ========================================================================
    #   Visual comparison

    # for angle in images:
    #
    #
    #     import alinea.phenomenal.reconstruction_3d_algorithm as algo
    #     c = algo.Cube(0, 0, 0, 10)
    #     cubes = list()
    #     cubes.append(c)
    #
    #     opencv_img = reconstruction_3d.re_projection_cubes_to_image(
    #         cubes, images[angle], opencv_calibration[angle])
    #
    #     # octree_img = reconstruction_3d.re_projection_octree_to_image(
    #     #     octree, images[angle], opencv_calibration[angle])
    #     #
    #     # manual_img = reconstruction_3d.manual_re_projection_cubes_to_image(
    #     #     manual_cubes, images[angle], manual_calibration, angle)
    #     #
    #     # tools_test.show_comparison_3_image(opencv_img,
    #     #                                    octree_img,
    #     #                                    manual_img)

          # tools_test.show_image(opencv_img)


def test_calibration_on_reconstruction_3d_2():
    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        angle = angles[i]

        if angle < 105:
            images[angle] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    opencv_calibration.print_value()
    calibration_tools.plot_vectors(opencv_calibration.rotation_vectors)
    calibration_tools.plot_vectors(opencv_calibration.translation_vectors)

    image_0_90 = dict()

    for angle in images:
        if angle <= 105:
            image_0_90[angle] = images[angle]

    opencv_cubes = reconstruction_3d.reconstruction_3d(
        images, opencv_calibration, 1)

    tools_test.show_cube(opencv_cubes, 1, "opencv_cubes")

    f = open('reconstruction_3d.xyz', 'w')
    for cube in opencv_cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f \n" % (x, y, z))

    f.close()

    #   ========================================================================
    #   Visual comparison

    for angle in images:

        opencv_img = reconstruction_3d.re_projection_cubes_to_image(
            opencv_cubes, images[angle], opencv_calibration[angle])

        tools_test.show_image(opencv_img, str(angle))


def test_calibration_on_reconstruction_3d_3():
    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        angle = angles[i]

        if angle < 105:
            images[angle] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    image_0_90 = dict()
    for angle in images:
        if angle <= 105:
            image_0_90[angle] = images[angle]

    opencv_cubes = reconstruction_3d.reconstruction_3d(
        images, opencv_calibration, 5)

    x_min = float("inf")
    y_min = float("inf")
    z_min = float("inf")

    x_max = - float("inf")
    y_max = - float("inf")
    z_max = - float("inf")

    for cube in opencv_cubes:
        x, y, z = cube.position[0, 0], cube.position[0, 1], cube.position[0, 2]

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)

        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)

    r = opencv_cubes[0].radius * 2
    print r
    print x_min, x_max, (x_max - x_min) / r
    print y_min, y_max, (y_max - y_min) / r
    print z_min, z_max, (z_max - z_min) / r

    x_r_min = x_min / r
    y_r_min = y_min / r
    z_r_min = z_min / r

    import numpy as np

    mat = np.zeros(
        (((x_max - x_min) / r) + 1,
         ((y_max - y_min) / r) + 1,
         ((z_max - z_min) / r) + 1))

    print mat.shape

    X = list()
    Y = list()
    Z = list()
    for cube in opencv_cubes:
        x, y, z = cube.position[0, 0], cube.position[0, 1], cube.position[0, 2]
        x_new = (x / r) - x_r_min
        y_new = (y / r) - y_r_min
        z_new = (z / r) - z_r_min


        print x_new, y_new, z_new

        X.append(np.uint8(x_new))
        Y.append(np.uint8(y_new))
        Z.append(np.uint8(z_new))

        mat[x_new, y_new, z_new] = 1

    xl, yl, zl = mat.shape
    print xl, yl, zl
    for i in range(zl):
        m = mat[:, :, i] * 255
        cv2.imwrite('./images/%d.png' % i, m)


    cubes = list()
    for (x, y, z), value in np.ndenumerate(mat):
        if mat[x, y, z] == 1:
            cube = reconstruction_3d_algorithm.Cube(x, y, z, 10)
            cubes.append(cube)

    tools_test.show_cube(cubes, 1)


def test_calibration_on_reconstruction_3d_4():
    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'

    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        angle = angles[i]

        if angle < 270:
            images[angle] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    opencv_calibration.print_value()
    calibration_tools.plot_vectors(opencv_calibration.rotation_vectors)
    calibration_tools.plot_vectors(opencv_calibration.translation_vectors)

    image_0_270 = dict()

    for angle in images:
        if angle <= 270:
            image_0_270[angle] = images[angle]

    opencv_cubes = reconstruction_3d.reconstruction_3d(
        images, opencv_calibration, 1)

    tools_test.show_cube(opencv_cubes, 1, "opencv_cubes")

    f = open('reconstruction_3d.xyz', 'w')
    for cube in opencv_cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f \n" % (x, y, z))

    f.close()

    #   ========================================================================
    #   Visual comparison

    for angle in images:

        opencv_img = reconstruction_3d.re_projection_cubes_to_image(
            opencv_cubes, images[angle], opencv_calibration[angle])

        tools_test.show_image(opencv_img, str(angle))


def test_pickle():
    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'my_calibration')

    opencv_calibration.write_calibration('my_calibration')


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_calibration()
    # test_calibration_2()
    # test_compute_rotation_and_translation_vectors()
    # test_calibration_on_reconstruction_3d()
    # test_calibration_on_reconstruction_3d_4()

    #test_re_projection()


