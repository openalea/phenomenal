# -*- python -*-
#
#       test_reconstruction_3d.py : 
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
import numpy
import cv2
import math

#       ========================================================================
#       Local Import
import alinea.phenomenal.result_viewer
import alinea.phenomenal.calibration_jerome
import alinea.phenomenal.reconstruction_3d
import alinea.phenomenal.reconstruction_3d_algorithm
import alinea.phenomenal.data_transformation
import alinea.phenomenal.misc


#       ========================================================================
#       Code

def build_object_1():

    matrix = numpy.ones((10, 10, 10), dtype=numpy.uint8)

    cubes = alinea.phenomenal.data_transformation.matrix_to_cubes(
        matrix, 8, [-472, -472, 200])

    return cubes


def build_image_from_cubes(cubes, calibration, step=30):

    images = dict()
    for angle in range(0, 360, step):
        img = numpy.zeros((2454, 2056), dtype=numpy.uint8)
        h, l = numpy.shape(img)

        print 'Build image angle : ', angle
        for cube in cubes:
            x_min, x_max, y_min, y_max = \
                alinea.phenomenal.reconstruction_3d_algorithm.bbox_projection(
                    cube, calibration, angle)

            x_min = min(max(x_min, 0), l - 1)
            x_max = min(max(x_max, 0), l - 1)
            y_min = min(max(y_min, 0), h - 1)
            y_max = min(max(y_max, 0), h - 1)

            img[y_min:y_max + 1, x_min:x_max + 1] = 255

        images[angle] = img

    return images


def test_cube():

    cube = alinea.phenomenal.reconstruction_3d_algorithm.Cube(
        0, 0, 0, 8)

    cubes = cube.oct_split()

    assert len(cubes) == 8

    assert (cubes[0].position == [-4., -4., -4.]).all()
    assert (cubes[1].position == [4., -4., -4.]).all()
    assert (cubes[2].position == [-4., 4., -4.]).all()
    assert (cubes[3].position == [-4., -4., 4.]).all()
    assert (cubes[4].position == [4., 4., -4.]).all()
    assert (cubes[5].position == [4., -4., 4.]).all()
    assert (cubes[6].position == [-4., 4., 4.]).all()
    assert (cubes[7].position == [4., 4., 4.]).all()


def test_reconstruction_1():

    cubes = build_object_1()

    # alinea.phenomenal.result_viewer.show_cubes(cubes, scale_factor=8)

    calibration = alinea.phenomenal.calibration_jerome.\
        Calibration.read_calibration('/tests/test_calibration_jerome')

    images = build_image_from_cubes(cubes, calibration, step=30)

    cubes = alinea.phenomenal.reconstruction_3d.reconstruction_3d(
        images, calibration, precision=8, verbose=True)

    mat = alinea.phenomenal.data_transformation.cubes_to_matrix(cubes)

    print numpy.shape(mat)

    assert mat.size == 1728
    assert (mat == 1).all()

    # alinea.phenomenal.result_viewer.show_cubes(cubes, scale_factor=8)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    # test_cube()
    test_reconstruction_1()
