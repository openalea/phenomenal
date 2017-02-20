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

from alinea.phenomenal.data_structure.image3d import Image3D
# ==============================================================================


def bounding_box(voxels_position):
    if not voxels_position:
        raise ValueError("Empty list")

    x_min = float("inf")
    y_min = float("inf")
    z_min = float("inf")

    x_max = - float("inf")
    y_max = - float("inf")
    z_max = - float("inf")

    for x, y, z in voxels_position:
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)

        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)

    return (x_min, y_min, z_min), (x_max, y_max, z_max)


def image_3d_to_voxels_position(image_3d,
                                voxels_value=1,
                                voxels_size=None,
                                world_coordinate=None):

    xx, yy, zz = numpy.where(image_3d >= voxels_value)

    if voxels_size is None:
        voxels_size = image_3d.voxels_size

    if world_coordinate is None:
        world_coordinate = image_3d.world_coordinate

    xxx = world_coordinate[0] + xx * voxels_size
    yyy = world_coordinate[1] + yy * voxels_size
    zzz = world_coordinate[2] + zz * voxels_size

    voxels_position = list()
    for i in range(len(xxx)):
        voxels_position.append((xxx[i], yyy[i], zzz[i]))

    return voxels_position, voxels_size


def voxels_position_to_image_3d(voxels_position, voxels_size):

    (x_min, y_min, z_min), (x_max, y_max, z_max) = bounding_box(voxels_position)

    len_x = int((x_max - x_min) / voxels_size + 1)
    len_y = int((y_max - y_min) / voxels_size + 1)
    len_z = int((z_max - z_min) / voxels_size + 1)

    image_3d = Image3D.zeros((len_x, len_y, len_z),
                             dtype=numpy.bool,
                             voxels_size=voxels_size,
                             world_coordinate=(x_min, y_min, z_min))

    for x, y, z in voxels_position:
        x_new = int((x - x_min) / voxels_size)
        y_new = int((y - y_min) / voxels_size)
        z_new = int((z - z_min) / voxels_size)

        image_3d[x_new, y_new, z_new] = 1

    return image_3d

