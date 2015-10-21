# -*- python -*-
#
#       multi_view_reconstruction.py :
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
#       ========================================================================

#       ========================================================================
#       External Import
import collections
import math
import numpy


#       ========================================================================
#       PROJECTION

def bbox_projection(point_3d, radius, calibration, angle):

    corners = corners_point_3d(point_3d, radius)

    ly = list()
    lx = list()

    for pt_3d in corners:
        x, y = calibration.project_point(pt_3d, angle)

        lx.append(x)
        ly.append(y)

    return min(lx), max(lx), min(ly), max(ly)


#       ========================================================================
#       Create and split cubes

def split_points_3d(points_3d, radius):

    if len(points_3d) == 0:
        return points_3d

    r = radius / 2.0

    l = collections.deque()
    while True:
        try:

            point_3d = points_3d.popleft()

            x_minus = point_3d[0] - r
            x_plus = point_3d[0] + r

            y_minus = point_3d[1] - r
            y_plus = point_3d[1] + r

            z_minus = point_3d[2] - r
            z_plus = point_3d[2] + r

            l.append((x_minus, y_minus, z_minus))
            l.append((x_plus, y_minus, z_minus))
            l.append((x_minus, y_plus, z_minus))
            l.append((x_minus, y_minus, z_plus))
            l.append((x_plus, y_plus, z_minus))
            l.append((x_plus, y_minus, z_plus))
            l.append((x_minus, y_plus, z_plus))
            l.append((x_plus, y_plus, z_plus))

        except IndexError:
            break

    return l


def corners_point_3d(point_3d, radius):

    x_minus = point_3d[0] - radius
    x_plus = point_3d[0] + radius

    y_minus = point_3d[1] - radius
    y_plus = point_3d[1] + radius

    z_minus = point_3d[2] - radius
    z_plus = point_3d[2] + radius

    l = list()

    l.append((x_minus, y_minus, z_minus))
    l.append((x_plus, y_minus, z_minus))
    l.append((x_minus, y_plus, z_minus))
    l.append((x_minus, y_minus, z_plus))
    l.append((x_plus, y_plus, z_minus))
    l.append((x_plus, y_minus, z_plus))
    l.append((x_minus, y_plus, z_plus))
    l.append((x_plus, y_plus, z_plus))

    return l


#       =======================================================================
#       Algorithm


def point_3d_is_in_image(image,
                         height_image,
                         length_image,
                         point_3d,
                         calibration,
                         angle,
                         radius):
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

    x, y = calibration.project_point(point_3d, angle)

    if (0 <= x < length_image and
        0 <= y < height_image and
            image[y, x] > 0):
        return True

    # =================================================================

    x_min, x_max, y_min, y_max = bbox_projection(point_3d,
                                                 radius,
                                                 calibration,
                                                 angle)

    x_min = min(max(math.floor(x_min), 0), length_image - 1)
    x_max = min(max(math.ceil(x_max), 0), length_image - 1)
    y_min = min(max(math.floor(y_min), 0), height_image - 1)
    y_max = min(max(math.ceil(y_max), 0), height_image - 1)

    if (image[y_min, x_min] > 0 or
        image[y_max, x_min] > 0 or
        image[y_min, x_max] > 0 or
            image[y_max, x_max] > 0):
        return True

    # ==================================================================

    if numpy.any(image[y_min:y_max + 1, x_min:x_max + 1] > 0):
        return True

    return False


def octree_builder_optimize(images, points, radius, calibration):
    kept = collections.deque()
    len_image = len(images)

    height_image, length_image = numpy.shape(images.itervalues().next())

    while True:
        try:
            point = points.popleft()

            no = 0
            yes = 0

            for angle in images:
                if point_3d_is_in_image(images[angle],
                                        height_image,
                                        length_image,
                                        point,
                                        calibration,
                                        angle,
                                        radius):
                    yes += 1
                else:
                    no += 1
                    break

            # if (len_image >= 10 and no <= 1) or no == 0:
            #     kept.append(cube)

            if no == 0:
                kept.append(point)

        except IndexError:
            break

    return kept


def octree_builder(image, points, radius, calibration, angle):

    kept = collections.deque()
    height_image, length_image = numpy.shape(image)

    while True:
        try:
            point = points.popleft()

            if point_3d_is_in_image(image,
                                    height_image,
                                    length_image,
                                    point,
                                    calibration,
                                    angle,
                                    radius):
                kept.append(point)

        except IndexError:
            break

    return kept


def project_points_on_image(points, radius, image, calibration, angle):

    height_image, length_image = numpy.shape(image)
    img = numpy.zeros((height_image, length_image))

    for point in points:
        x_min, x_max, y_min, y_max = bbox_projection(point,
                                                     radius,
                                                     calibration,
                                                     angle)

        x_min = min(max(math.floor(x_min), 0), length_image - 1)
        x_max = min(max(math.ceil(x_max), 0), length_image - 1)
        y_min = min(max(math.floor(y_min), 0), height_image - 1)
        y_max = min(max(math.ceil(y_max), 0), height_image - 1)

        img[y_min:y_max + 1, x_min:x_max + 1] = 255

    return img


def reconstruction_3d(images, calibration, precision=4, verbose=False):

    if len(images) == 0:
        return None

    origin_point = (0.0, 0.0, 0.0)
    origin_radius = 2048

    points_3d = collections.deque()
    points_3d.append(origin_point)

    nb_iteration = 0
    while precision < origin_radius:
        precision *= 2
        nb_iteration += 1

    radius = precision
    for i in range(nb_iteration):

        points_3d = split_points_3d(points_3d, radius)
        radius /= 2.0

        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration, ' : ', len(points_3d)

        for angle in images:
            points_3d = octree_builder(images[angle],
                                       points_3d,
                                       radius,
                                       calibration,
                                       angle)

            if verbose is True:
                print 'Angle %d : %d' % (angle, len(points_3d))

    return points_3d


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    pass
