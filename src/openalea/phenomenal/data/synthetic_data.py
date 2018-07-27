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
import cv2

from ..object import Image3D, VoxelGrid
# ==============================================================================

__all__ = ["bin_images_with_circle", "build_cube"]

# ==============================================================================


def bin_images_with_circle(shape_image=(2454, 2056),
                           circle_position=(1227, 1028),
                           circle_radius=100):

    images = dict()
    for angle in range(0, 360, 30):
        img = numpy.zeros(shape_image, dtype=numpy.uint8)
        cv2.circle(img, circle_position, circle_radius, 255, -1)
        images[angle] = img

    return images


def build_cube(cube_size, voxels_size, voxels_position):

    image_3d = Image3D.ones((cube_size, cube_size, cube_size),
                            dtype=numpy.uint8,
                            voxels_size=voxels_size,
                            world_coordinate=voxels_position)

    return VoxelGrid.from_image_3d(image_3d).voxels_position
