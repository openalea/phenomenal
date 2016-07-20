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


def image_3d_to_voxel_centers(image_3d, voxel_value=1):
    xx, yy, zz = numpy.where(image_3d == voxel_value)

    xxx = image_3d.world_coordinate[0] + xx * image_3d.voxel_size
    yyy = image_3d.world_coordinate[1] + yy * image_3d.voxel_size
    zzz = image_3d.world_coordinate[2] + zz * image_3d.voxel_size

    voxel_centers = list()
    for i in range(len(xxx)):
        voxel_centers.append((xxx[i], yyy[i], zzz[i]))

    return voxel_centers, image_3d.voxel_size


def voxel_centers_to_image_3d(voxel_centers, voxel_size):
    """

    Args:
        voxel_centers:
        voxel_size:

    Returns:
        Image3D object

    """
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
