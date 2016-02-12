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
import os
import collections
import numpy
import cv2
# ==============================================================================


def change_orientation(cubes):
    for cube in cubes:
        x = cube.position[0]
        y = - cube.position[2]
        z = - cube.position[1]

        cube.position[0] = x
        cube.position[1] = y
        cube.position[2] = z

    return cubes


def save_matrix_like_stack_image(matrix, data_directory):

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    xl, yl, zl = matrix.shape
    print xl, yl, zl
    for i in range(zl):
        mat = matrix[:, :, i] * 255
        cv2.imwrite(data_directory + '%d.png' % i, mat)


def limit_points_3d(voxel_centers):

    if not voxel_centers:
        return None, None, None, None, None, None

    x_min = float("inf")
    y_min = float("inf")
    z_min = float("inf")

    x_max = - float("inf")
    y_max = - float("inf")
    z_max = - float("inf")

    for x, y, z in voxel_centers:

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)

        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)

    return x_min, y_min, z_min, x_max, y_max, z_max


def index_to_points_3d(index, voxel_size, origin=(0, 0, 0)):

    points_3d = collections.deque()
    ind = index.__copy__()
    while True:
        try:
            x, y, z = ind.popleft()
            pt_3d = (x * voxel_size + origin[0],
                     y * voxel_size + origin[1],
                     z * voxel_size + origin[2])
            points_3d.append(pt_3d)

        except IndexError:
            break

    return points_3d


def matrix_to_points_3d(matrix, voxel_size, origin=(0, 0, 0)):

    points_3d = list()
    for (x, y, z), value in numpy.ndenumerate(matrix):
        if value == 1 or value == 111:

            pt_3d = (origin[0] + x * voxel_size,
                     origin[1] + y * voxel_size,
                     origin[2] + z * voxel_size)

            points_3d.append(pt_3d)

    return points_3d


def matrix_to_points_3d_2(matrix, voxel_size, origin=(0, 0, 0)):

    points_3d = list()
    points_3d_leaf = list()
    for (x, y, z), value in numpy.ndenumerate(matrix):
        if value == 1:

            pt_3d = (origin[0] + x * voxel_size,
                     origin[1] + y * voxel_size,
                     origin[2] + z * voxel_size)

            points_3d.append(pt_3d)

    for (x, y, z), value in numpy.ndenumerate(matrix):
        if value == 111:

            pt_3d = (origin[0] + x * voxel_size,
                     origin[1] + y * voxel_size,
                     origin[2] + z * voxel_size)

            points_3d_leaf.append(pt_3d)

    return points_3d, points_3d_leaf


def points_3d_to_matrix(voxel_centers, voxel_size):

    if not voxel_centers:
        return numpy.zeros((0, 0, 0)), list(), (None, None, None)

    x_min, y_min, z_min, x_max, y_max, z_max = limit_points_3d(voxel_centers)

    x_r_min = x_min / voxel_size
    y_r_min = y_min / voxel_size
    z_r_min = z_min / voxel_size

    mat = numpy.zeros((round((x_max - x_min) / voxel_size) + 1,
                       round((y_max - y_min) / voxel_size) + 1,
                       round((z_max - z_min) / voxel_size) + 1),
                      dtype=numpy.uint8)

    index = collections.deque()
    for x, y, z in voxel_centers:
        x_new = (x / voxel_size) - x_r_min
        y_new = (y / voxel_size) - y_r_min
        z_new = (z / voxel_size) - z_r_min

        mat[x_new, y_new, z_new] = 1

        index.append((x_new, y_new, z_new))

    return mat, index, (x_min, y_min, z_min)


def points_3d_to_matrix_2(voxel_centers, points_3d_leaf, voxel_size):
    x_min, y_min, z_min, x_max, y_max, z_max = limit_points_3d(voxel_centers)

    for i in points_3d_leaf:
        x, y, z, xm, ym, zm = limit_points_3d(points_3d_leaf[i])

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)
        x_max = max(x_max, xm)
        y_max = max(y_max, ym)
        z_max = max(z_max, zm)

    x_r_min = x_min / voxel_size
    y_r_min = y_min / voxel_size
    z_r_min = z_min / voxel_size

    mat = numpy.zeros((round((x_max - x_min) / voxel_size) + 1,
                       round((y_max - y_min) / voxel_size) + 1,
                       round((z_max - z_min) / voxel_size) + 1),
                      dtype=numpy.uint8)

    index = collections.deque()
    for x, y, z in voxel_centers:
        x_new = (x / voxel_size) - x_r_min
        y_new = (y / voxel_size) - y_r_min
        z_new = (z / voxel_size) - z_r_min

        mat[x_new, y_new, z_new] = 1

        # index.append((x_new, y_new, z_new))

    nb = 2
    for i in points_3d_leaf:
        for x, y, z in points_3d_leaf[i]:
            x_new = (x / voxel_size) - x_r_min
            y_new = (y / voxel_size) - y_r_min
            z_new = (z / voxel_size) - z_r_min

            mat[x_new, y_new, z_new] = nb

            index.append((x_new, y_new, z_new))
        nb += 1

    return mat, index, (x_min, y_min, z_min)


def remove_internal_points_3d(voxel_centers, voxel_size):

    if not voxel_centers:
        return voxel_centers

    matrix, index, origin = points_3d_to_matrix(voxel_centers, voxel_size)

    index_new = collections.deque()
    mat = matrix.copy()
    while True:
        try:
            x, y, z = index.popleft()

            if (matrix[x - 1, y - 1, z] == 1 and
                matrix[x - 1, y, z] == 1 and
                matrix[x - 1, y + 1, z] == 1 and
                matrix[x, y - 1, z] == 1 and
                matrix[x, y + 1, z] == 1 and
                matrix[x + 1, y - 1, z] == 1 and
                matrix[x + 1, y, z] == 1 and
                matrix[x + 1, y + 1, z] == 1 and

                matrix[x - 1, y - 1, z - 1] == 1 and
                matrix[x - 1, y, z - 1] == 1 and
                matrix[x - 1, y + 1, z - 1] == 1 and
                matrix[x, y - 1, z - 1] == 1 and
                matrix[x, y, z - 1] == 1 and
                matrix[x, y + 1, z - 1] == 1 and
                matrix[x + 1, y - 1, z - 1] == 1 and
                matrix[x + 1, y, z - 1] == 1 and
                matrix[x + 1, y + 1, z - 1] == 1 and

                matrix[x - 1, y - 1, z + 1] == 1 and
                matrix[x - 1, y, z + 1] == 1 and
                matrix[x - 1, y + 1, z + 1] == 1 and
                matrix[x, y - 1, z + 1] == 1 and
                matrix[x, y, z + 1] == 1 and
                matrix[x, y + 1, z + 1] == 1 and
                matrix[x + 1, y - 1, z + 1] == 1 and
                matrix[x + 1, y, z + 1] == 1 and
                    matrix[x + 1, y + 1, z + 1] == 1):
                mat[x, y, z] = 0
            else:
                index_new.append((x, y, z))

        except IndexError:

            if len(index) > 0:
                index_new.append((x, y, z))
                continue
            else:
                break

    return index_to_points_3d(index_new, voxel_size, origin=origin)
