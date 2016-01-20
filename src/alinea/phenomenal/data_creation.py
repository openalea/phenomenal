# -*- python -*-
#
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

import alinea.phenomenal.data_transformation
import alinea.phenomenal.multi_view_reconstruction
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


def build_object_1(size, radius, origin):

    matrix = numpy.ones((size, size, size), dtype=numpy.uint8)

    points_3d = alinea.phenomenal.data_transformation.matrix_to_points_3d(
        matrix, radius, origin)

    return points_3d


def build_image_from_points_3d(points_3d, radius, projection,
                               start=0,
                               stop=360,
                               step=30):

    images = dict()
    for angle in range(start, stop, step):
        img = numpy.zeros((2454, 2056), dtype=numpy.uint8)
        h, l = numpy.shape(img)

        print 'Build image angle : ', angle
        for point_3d in points_3d:
            x_min, x_max, y_min, y_max = \
                alinea.phenomenal.multi_view_reconstruction.bbox_projection(
                    point_3d, radius, projection, angle)

            x_min = min(max(x_min, 0), l - 1)
            x_max = min(max(x_max, 0), l - 1)
            y_min = min(max(y_min, 0), h - 1)
            y_max = min(max(y_max, 0), h - 1)

            img[y_min:y_max + 1, x_min:x_max + 1] = 255

        images[angle] = img

    return images

