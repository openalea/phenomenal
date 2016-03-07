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
import numpy
import vtk
from vtk.util.numpy_support import get_vtk_array_type
from operator import itemgetter


# ==============================================================================
# VTK Transformation

def voxel_centers_to_vtk_image_data(voxel_centers, voxel_size):
    x_min = min(voxel_centers, key=itemgetter(0))[0]
    x_max = max(voxel_centers, key=itemgetter(0))[0]

    y_min = min(voxel_centers, key=itemgetter(1))[1]
    y_max = max(voxel_centers, key=itemgetter(1))[1]

    z_min = min(voxel_centers, key=itemgetter(2))[2]
    z_max = max(voxel_centers, key=itemgetter(2))[2]

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(int((x_max - x_min) / voxel_size + 1),
                             int((y_max - y_min) / voxel_size + 1),
                             int((z_max - z_min) / voxel_size + 1))
    image_data.SetSpacing(1.0, 1.0, 1.0)
    image_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    for x, y, z in voxel_centers:
        nx = int((x - x_min) / voxel_size)
        ny = int((y - y_min) / voxel_size)
        nz = int((z - z_min) / voxel_size)

        image_data.SetScalarComponentFromDouble(
            nx, ny, nz, 0, 1)

    return image_data


def numpy_matrix_to_vtk_image_data(data_matrix):
    nx, ny, nz = data_matrix.shape

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(nx, ny, nz)
    image_data.SetSpacing(1.0, 1.0, 1.0)
    image_data.AllocateScalars(get_vtk_array_type(data_matrix.dtype), 1)

    lx, ly, lz = image_data.GetDimensions()
    for i in xrange(0, lx):
        for j in xrange(0, ly):
            for k in xrange(0, lz):
                image_data.SetScalarComponentFromDouble(
                    i, j, k, 0, data_matrix[i, j, k])

    return image_data


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


def matrix_to_points_3d(matrix, voxel_size,
                        origin=(0, 0, 0),
                        voxel_value=1):

    xx, yy, zz = numpy.where(matrix == voxel_value)

    xxx = origin[0] + xx * voxel_size
    yyy = origin[1] + yy * voxel_size
    zzz = origin[2] + zz * voxel_size

    points_3d = list()
    for i in xrange(len(xxx)):
        points_3d.append((xxx[i], yyy[i], zzz[i]))

    return points_3d


def points_3d_to_matrix(voxel_centers, voxel_size):

    if not voxel_centers:
        return numpy.zeros((0, 0, 0)), list(), (None, None, None)

    x_min, y_min, z_min, x_max, y_max, z_max = limit_points_3d(voxel_centers)

    mat = numpy.zeros(((x_max - x_min) / voxel_size + 1,
                       (y_max - y_min) / voxel_size + 1,
                       (z_max - z_min) / voxel_size + 1),
                      dtype=numpy.uint8)

    for x, y, z in voxel_centers:
        x_new = (x - x_min) / voxel_size
        y_new = (y - y_min) / voxel_size
        z_new = (z - z_min) / voxel_size

        mat[x_new, y_new, z_new] = 1

    return mat, (x_min, y_min, z_min)


def remove_internal_points_3d(voxel_centers, voxel_size):

    if not voxel_centers:
        return voxel_centers

    matrix, origin = points_3d_to_matrix(voxel_centers, voxel_size)

    xx, yy, zz = numpy.where(matrix[1:-1, 1:-1, 1:-1] == 1)

    xx += 1
    yy += 1
    zz += 1

    def is_removable(x, y, z):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if matrix[x + i, y + j, z + k] == 0:
                        return False
        return True

    mat = matrix.copy()
    for i in xrange(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]
        if is_removable(x, y, z):
            mat[x, y, z] = 0

    voxel_centers = matrix_to_points_3d(mat, voxel_size, origin=origin)

    return voxel_centers


def find_position_base_plant(matrix, origin, voxel_size, neighbor_size=2):

    x = int(round(-origin[0] / voxel_size))
    y = int(round(-origin[1] / voxel_size))

    k = neighbor_size
    roi = matrix[x - k: x + k, y - k: y + k, :]

    xx, yy, zz = numpy.where(roi == 1)
    i = numpy.argmin(zz)

    return x - k + xx[i], y - k + yy[i], zz[i]


def labeling_matrix(matrix):

    len_x, len_y, len_z = matrix.shape

    mm = numpy.zeros((len_x + 2, len_y + 2, len_z + 2))
    mm[1:-1, 1:-1, 1:-1] = matrix

    xx, yy, zz = numpy.where(mm == 1)
    mat = numpy.zeros_like(mm, dtype=int)

    def get_neighbors(x, y, z):
        l = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    ind = x + i, y + j, z + k
                    if mm[ind] == 1:
                        l.append(ind)
        return l

    print len(xx)

    num_label = 1
    for i in xrange(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]

        if mat[x, y, z] == 0:
            mat[x, y, z] = num_label
            neighbors = get_neighbors(x, y, z)
            while neighbors:
                xxx, yyy, zzz = neighbors.pop()

                if mat[xxx, yyy, zzz] == 0:
                    mat[xxx, yyy, zzz] = num_label
                    neighbors += get_neighbors(xxx, yyy, zzz)

            num_label += 1

    return mat[1:-1, 1:-1, 1:-1]
