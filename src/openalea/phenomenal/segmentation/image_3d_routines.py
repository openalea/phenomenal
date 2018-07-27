# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import numpy

from ..object import Image3D
# ==============================================================================


def remove_internal(image_3d):
    len_x, len_y, len_z = image_3d.shape
    im = Image3D.zeros((len_x + 2, len_y + 2, len_z + 2),
                       voxels_size=image_3d.voxels_size)
    im[1:-1, 1:-1, 1:-1] = image_3d

    xx, yy, zz = numpy.where(image_3d == 1)

    ijk = [(-1, -1, -1), (-1, -1, 0), (-1, -1, 1),
           (-1, 0, -1), (-1, 0, 0), (-1, 0, 1),
           (-1, 1, -1), (-1, 1, 0), (-1, 1, 1),
           (0, -1, -1), (0, -1, 0), (0, -1, 1),
           (0, 0, -1), (0, 0, 0), (0, 0, 1),
           (0, 1, -1), (0, 1, 0), (0, 1, 1),
           (1, -1, -1), (1, -1, 0), (1, -1, 1),
           (1, 0, -1), (1, 0, 0), (1, 0, 1),
           (1, 1, -1), (1, 1, 0), (1, 1, 1)]

    def removable(x, y, z):
        for i, j, k in ijk:
            if im[x + i, y + j, z + k] == 0:
                return False
        return True

    im2 = Image3D.zeros_like(im)
    for i in range(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]
        if removable(x, y, z):
            im2[(x, y, z)] = 1

    result = im - im2

    return result[1:-1, 1:-1, 1:-1]


def labeling_connected_component(image_3d):
    len_x, len_y, len_z = image_3d.shape

    im = Image3D.zeros((len_x + 2, len_y + 2, len_z + 2))
    im[1:-1, 1:-1, 1:-1] = image_3d

    xx, yy, zz = numpy.where(im == 1)

    mat = Image3D.zeros_like(im)

    def get_neighbors(x, y, z):
        l = list()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    ind = x + i, y + j, z + k
                    if im[ind] == 1:
                        l.append(ind)
        return l

    num_label = 1
    for i in range(len(xx)):
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


def kept_biggest_connected_component(image_3d):
    mat = labeling_connected_component(image_3d)

    max_value = 0
    save = None
    for i in range(1, numpy.max(mat) + 1):
        nb = len(numpy.where(mat == i)[0])
        if nb > max_value:
            max_value = nb
            save = i

    mat[mat != save] = 0
    mat[mat == save] = 1

    return mat
