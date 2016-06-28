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
import numpy

from alinea.phenomenal.multi_view_reconstruction.image3d import Image3D
# ==============================================================================


def bounding_box(voxel_centers):

    if not voxel_centers:
        raise ValueError("Empty list")

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

    return (x_min, y_min, z_min), (x_max, y_max, z_max)


def remove_internal(image_3d):

    len_x, len_y, len_z = image_3d.shape
    im = Image3D.zeros((len_x + 2, len_y + 2, len_z + 2))
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
    for i in xrange(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]
        if removable(x, y, z):
            im2[(x, y, z)] = 1

    result = im - im2

    return result[1:-1, 1:-1, 1:-1]


def find_position_base_plant(image_3d, neighbor_size=5):
    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxel_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxel_size))

    k = neighbor_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[max(x - k, 0): min(x + k, x_len),
                   max(y - k, 0): min(y + k, y_len),
                   :]

    xx, yy, zz = numpy.where(roi == 1)
    i = numpy.argmin(zz)

    return x - k + xx[i], y - k + yy[i], zz[i]


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


def biggest_connected_component(image_3d):
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


def image_3d_to_voxel_centers(image_3d, voxel_value=1):
    xx, yy, zz = numpy.where(image_3d == voxel_value)

    xxx = image_3d.world_coordinate[0] + xx * image_3d.voxel_size
    yyy = image_3d.world_coordinate[1] + yy * image_3d.voxel_size
    zzz = image_3d.world_coordinate[2] + zz * image_3d.voxel_size

    voxel_centers = list()
    for i in xrange(len(xxx)):
        voxel_centers.append((xxx[i], yyy[i], zzz[i]))

    return voxel_centers, image_3d.voxel_size


def voxel_centers_to_image_3d(voxel_centers, voxel_size):
    (x_min, y_min, z_min), (x_max, y_max, z_max) = bounding_box(voxel_centers)

    len_x = int((x_max - x_min) / voxel_size + 1)
    len_y = int((y_max - y_min) / voxel_size + 1)
    len_z = int((z_max - z_min) / voxel_size + 1)

    image_3d = Image3D.zeros((len_x, len_y, len_z),
                             dtype=numpy.bool,
                             voxel_size=voxel_size,
                             world_coordinate=(x_min, y_min, z_min))

    for x, y, z in voxel_centers:
        x_new = int((x - x_min) / voxel_size)
        y_new = int((y - y_min) / voxel_size)
        z_new = int((z - z_min) / voxel_size)

        image_3d[x_new, y_new, z_new] = 1

    return image_3d
