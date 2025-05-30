# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import numpy
from skimage.draw import disk

from ..object import Image3D, VoxelGrid
# ==============================================================================

__all__ = ["bin_images_with_circle", "build_cube", "random_voxel_grid"]

# ==============================================================================


def bin_images_with_circle(
    shape_image=(2454, 2056), circle_position=(1227, 1028), circle_radius=100
):
    images = {}
    for angle in range(0, 360, 30):
        img = numpy.zeros(shape_image, dtype=numpy.uint8)
        rr, cc = disk(circle_position, circle_radius)
        img[rr, cc] = 255
        images[angle] = img

    return images


def build_cube(cube_size, voxels_size, voxels_position):
    image_3d = Image3D.ones(
        (cube_size, cube_size, cube_size),
        dtype=numpy.uint8,
        voxels_size=voxels_size,
        world_coordinate=voxels_position,
    )

    return VoxelGrid.from_image_3d(image_3d).voxels_position


def random_voxel_grid(shape=(10, 15, 5), voxels_size=16, int_choice=1000):
    voxels_position = numpy.array(list(numpy.ndindex(shape))) * voxels_size
    voxels_position = voxels_position.astype(float)
    numpy.random.shuffle(voxels_position)

    return VoxelGrid(voxels_position[:int_choice], voxels_size)
