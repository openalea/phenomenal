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

from alinea.phenomenal.data_structure import (
    Image3D,
    image_3d_to_voxel_centers)

# ==============================================================================

__all__ = ["write_circle_on_image", "build_images_1", "build_object_1"]

# ==============================================================================


def write_circle_on_image(image, y_position, x_position, size):

    for i in range(0, size):
        image[y_position - i, x_position - i: x_position + i] = 255

    i += 1
    for j in range(size, -1, -1):
        image[y_position - i, x_position - j: x_position + j] = 255
        i += 1

    return image


def build_images_1():

    images = dict()
    for angle in range(0, 360, 30):
        img = numpy.zeros((2454, 2056), dtype=numpy.uint8)
        img = write_circle_on_image(img, 2454 // 2, 2056 // 2, 100)
        images[angle] = img

    return images


def build_object_1(size, voxel_size, world_coordinate):

    image_3d = Image3D.ones((size, size, size),
                            dtype=numpy.uint8,
                            voxel_size=voxel_size,
                            world_coordinate=world_coordinate)

    return image_3d_to_voxel_centers(image_3d)
