# -*- python -*-
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
# ==============================================================================
import numpy


from alinea.phenomenal.data_transformation import (
    matrix_to_points_3d)
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


def build_object_1(size, voxel_size, voxel_center_origin):

    matrix = numpy.ones((size, size, size), dtype=numpy.uint8)

    voxel_centers = matrix_to_points_3d(matrix,
                                        voxel_size,
                                        voxel_center_origin)

    return voxel_centers
