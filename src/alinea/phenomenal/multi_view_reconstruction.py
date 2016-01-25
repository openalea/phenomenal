# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
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
import collections
import math
import numpy
# ==============================================================================


def get_bounding_box_voxel_projected(voxel_center, voxel_size, projection):
    """
    Compute the bounding box value according the radius, angle and calibration
    parameters of point_3d projection

    Parameters
    ----------
    voxel_center : (x, y, z)

    voxel_size : float

    projection : function ((x, y, z)) -> (x, y)

    Returns
    -------
    out : (x_min, x_max, y_min, y_max)
        Containing min and max value of point_3d projection in x and y axes.
    """

    voxel_corners = get_voxel_corners(voxel_center, voxel_size)

    lx = list()
    ly = list()
    for voxel_corner in voxel_corners:
        x, y = projection(voxel_corner)

        lx.append(x)
        ly.append(y)

    return min(lx), max(lx), min(ly), max(ly)


def get_voxel_corners(voxel_center, voxel_size):
    """
    
    :param voxel_center:
    :param voxel_size:
    :return:
    """

    r = voxel_size / 2.0

    x_minus = voxel_center[0] - r
    x_plus = voxel_center[0] + r

    y_minus = voxel_center[1] - r
    y_plus = voxel_center[1] + r

    z_minus = voxel_center[2] - r
    z_plus = voxel_center[2] + r

    return [(x_minus, y_minus, z_minus),
            (x_plus, y_minus, z_minus),
            (x_minus, y_plus, z_minus),
            (x_minus, y_minus, z_plus),
            (x_plus, y_plus, z_minus),
            (x_plus, y_minus, z_plus),
            (x_minus, y_plus, z_plus),
            (x_plus, y_plus, z_plus)]

# ==============================================================================


def split_voxel_centers_in_eight(voxel_centers, voxel_size):

    if len(voxel_centers) == 0:
        return voxel_centers

    r = voxel_size / 4.0

    l = collections.deque()
    for voxel_center in voxel_centers:

        x_minus = voxel_center[0] - r
        x_plus = voxel_center[0] + r

        y_minus = voxel_center[1] - r
        y_plus = voxel_center[1] + r

        z_minus = voxel_center[2] - r
        z_plus = voxel_center[2] + r

        l.extend([(x_minus, y_minus, z_minus),
                  (x_plus, y_minus, z_minus),
                  (x_minus, y_plus, z_minus),
                  (x_minus, y_minus, z_plus),
                  (x_plus, y_plus, z_minus),
                  (x_plus, y_minus, z_plus),
                  (x_minus, y_plus, z_plus),
                  (x_plus, y_plus, z_plus)])

    return l


def split_voxel_centers_in_four(voxel_centers, voxel_size):

    if len(voxel_centers) == 0:
        return voxel_centers

    r = voxel_size / 4.0

    l = collections.deque()
    for voxel_center in voxel_centers:
        x = voxel_center[0]

        y_minus = voxel_center[1] - r
        y_plus = voxel_center[1] + r

        z_minus = voxel_center[2] - r
        z_plus = voxel_center[2] + r

        l.extend([(x, y_minus, z_minus),
                  (x, y_minus, z_plus),
                  (x, y_plus, z_minus),
                  (x, y_plus, z_plus)])

    return l

# ==============================================================================


def voxel_is_visible_in_image(voxel_center,
                              voxel_size,
                              image,
                              projection):
    """
    Algorithm
    =========

    For each cube in cubes :
        - Project center cube position on image:
        - Kept the cube and pass to the next if :
            + The pixel value of center position projected is > 0

        - Compute the bounding box and project the positions on image
        - Kept the cube and pass to the next if :
            + The pixel value of extremity of bounding box projected is > 0

        - Kept the cube and pass to the next if :
            + Any pixel value in the bounding box projected is > 0
    """

    height_image, length_image = image.shape
    x, y = projection(voxel_center)

    if (0 <= x < length_image and
        0 <= y < height_image and
            image[y, x] > 0):
        return True

    # ==========================================================================

    x_min, x_max, y_min, y_max = get_bounding_box_voxel_projected(
        voxel_center, voxel_size, projection)

    x_min = min(max(math.floor(x_min), 0), length_image - 1)
    x_max = min(max(math.ceil(x_max), 0), length_image - 1)
    y_min = min(max(math.floor(y_min), 0), height_image - 1)
    y_max = min(max(math.ceil(y_max), 0), height_image - 1)

    if (image[y_min, x_min] > 0 or
        image[y_max, x_min] > 0 or
        image[y_min, x_max] > 0 or
            image[y_max, x_max] > 0):
        return True

    # ==========================================================================

    if numpy.any(image[y_min:y_max + 1, x_min:x_max + 1] > 0):
        return True


def kept_visible_voxel(voxel_centers,
                       voxel_size,
                       images_projections,
                       error_tolerance):

    kept = collections.deque()
    for voxel_center in voxel_centers:
        negative_weight = 0
        for image, projection in images_projections:
            if not voxel_is_visible_in_image(
                    voxel_center, voxel_size, image, projection):
                negative_weight += 1
                if negative_weight > error_tolerance:
                    break

        if negative_weight <= error_tolerance:
            kept.append(voxel_center)

    return kept

# ==============================================================================


def reconstruction_3d(images_projections,
                      voxel_size=4,
                      error_tolerance=0,
                      voxel_center_origin=(0.0, 0.0, 0.0),
                      voxel_centers=None,
                      verbose=False):

    if len(images_projections) == 0:
        return

    origin_radius = 2048 * 2

    if voxel_centers is None:
        voxel_centers = collections.deque()
        voxel_centers.append(voxel_center_origin)

    nb_iteration = 0

    while voxel_size < origin_radius:
        voxel_size *= 2.0
        nb_iteration += 1

    for i in range(nb_iteration):
        if len(images_projections) == 1:
            voxel_centers = split_voxel_centers_in_four(voxel_centers,
                                                        voxel_size)
        else:
            voxel_centers = split_voxel_centers_in_eight(voxel_centers,
                                                         voxel_size)

        voxel_size /= 2.0

        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration,
            print ' : ', len(voxel_centers),

        voxel_centers = kept_visible_voxel(
            voxel_centers, voxel_size, images_projections, error_tolerance)

        if verbose is True:
            print ' - ', len(voxel_centers)

    return voxel_centers

# ==============================================================================


def project_voxel_centers_on_image(voxel_centers,
                                   voxel_size,
                                   shape_image,
                                   projection):

    height_image, length_image = shape_image
    img = numpy.zeros((height_image, length_image), dtype=numpy.uint8)

    for voxel_center in voxel_centers:
        x_min, x_max, y_min, y_max = get_bounding_box_voxel_projected(
            voxel_center, voxel_size, projection)

        x_min = min(max(math.floor(x_min), 0), length_image - 1)
        x_max = min(max(math.ceil(x_max), 0), length_image - 1)
        y_min = min(max(math.floor(y_min), 0), height_image - 1)
        y_max = min(max(math.ceil(y_max), 0), height_image - 1)

        img[y_min:y_max + 1, x_min:x_max + 1] = 255

    return img


def error_projection(image,
                     projection,
                     voxel_centers,
                     voxel_size):

    img = project_voxel_centers_on_image(
        voxel_centers, voxel_size, image.shape, projection)

    img = numpy.subtract(img, image)
    img[img == -255] = 255

    return numpy.count_nonzero(img)
