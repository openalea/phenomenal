# -*- python -*-
#
#       data_transformation.py :
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
import os
import cv2

#       ========================================================================
#       Local Import 
import alinea.phenomenal.reconstruction_3d_algorithm
#       ========================================================================
#       Code


def save_matrix_like_stack_image(matrix, data_directory):

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    xl, yl, zl = matrix.shape
    print xl, yl, zl
    for i in range(zl):
        mat = matrix[:, :, i] * 255
        cv2.imwrite(data_directory + '%d.png' % i, mat)


def limit_cubes(cubes):
    x_min = float("inf")
    y_min = float("inf")
    z_min = float("inf")

    x_max = - float("inf")
    y_max = - float("inf")
    z_max = - float("inf")

    for cube in cubes:
        x, y, z = cube.position[0], cube.position[1], cube.position[2]

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)

        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)

    return x_min, y_min, z_min, x_max, y_max, z_max


def matrix_to_cubes(matrix, radius, position):

    cubes = list()
    for (x, y, z), value in numpy.ndenumerate(matrix):
        if value == 1:
            cubes.append(alinea.phenomenal.reconstruction_3d_algorithm.Cube(
                position[0] + x * radius * 2,
                position[1] + y * radius * 2,
                position[2] + z * radius * 2, radius))

    return cubes


def cubes_to_matrix(cubes):

    x_min, y_min, z_min, x_max, y_max, z_max = limit_cubes(cubes)

    r = cubes[0].radius * 2

    x_r_min = x_min / r
    y_r_min = y_min / r
    z_r_min = z_min / r

    mat = numpy.zeros((((x_max - x_min) / r) + 1,
                       ((y_max - y_min) / r) + 1,
                       ((z_max - z_min) / r) + 1), dtype=numpy.uint8)

    X = list()
    Y = list()
    Z = list()

    for cube in cubes:
        x, y, z = cube.position[0], cube.position[1], cube.position[2]
        x_new = (x / r) - x_r_min
        y_new = (y / r) - y_r_min
        z_new = (z / r) - z_r_min

        X.append(numpy.uint8(x_new))
        Y.append(numpy.uint8(y_new))
        Z.append(numpy.uint8(z_new))

        mat[x_new, y_new, z_new] = 1

    return mat
#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
