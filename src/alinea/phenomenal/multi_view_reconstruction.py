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
# ==============================================================================

import collections
import math
import numpy


# ==============================================================================
# PROJECTION


def bbox_projection(point_3d, radius, projection, angle):
    """
    Compute the bounding box value according the radius, angle and calibration
    parameters of point_3d projection

    Parameters
    ----------
    point_3d : collections.deque

    radius : float

    calibration : object with project_point function

    angle : float

    Returns
    -------
    Tuple
        Containing min and max value of point_3d projection in x and y axes.
    """

    corners = corners_point_3d(point_3d, radius)

    res = projection.project_points(corners, angle)

    lx = res[:, 0]
    ly = res[:, 1]

    return min(lx), max(lx), min(ly), max(ly)


# ==============================================================================
# Create and split cubes

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


def split_points_3d_plan(points_3d, radius):

    if len(points_3d) == 0:
        return points_3d

    r = radius / 2.0

    l = collections.deque()
    while True:
        try:

            point_3d = points_3d.popleft()

            x = point_3d[0]

            y_minus = point_3d[1] - r
            y_plus = point_3d[1] + r

            z_minus = point_3d[2] - r
            z_plus = point_3d[2] + r

            l.append((x, y_minus, z_minus))
            l.append((x, y_minus, z_plus))
            l.append((x, y_plus, z_minus))
            l.append((x, y_plus, z_plus))

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


# ==============================================================================
# Algorithm


def point_3d_is_in_image(image,
                         height_image,
                         length_image,
                         point_3d,
                         projection,
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

    x, y = projection.project_point(point_3d, angle)

    if (0 <= x < length_image and
        0 <= y < height_image and
            image[y, x] > 0):
        return True

    # ==========================================================================

    x_min, x_max, y_min, y_max = bbox_projection(
        point_3d, radius, projection, angle)

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


def octree_builder(images, points, radius, projection):
    kept = collections.deque()

    height_image, length_image = numpy.shape(images.itervalues().next())

    error_tolerance = 0

    if len(images) >= 10:
        error_tolerance = 0

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
                                        projection,
                                        angle,
                                        radius):
                    yes += 1
                else:
                    no += 1
                    if no > error_tolerance:
                        break

            if no <= error_tolerance:
                kept.append(point)

        except IndexError:
            break

    return kept


def project_points_on_image(my_points, radius, shape_image, projection, angle):

    height_image, length_image = shape_image
    img = numpy.zeros((height_image, length_image))

    for point in my_points:
        x_min, x_max, y_min, y_max = bbox_projection(point,
                                                     radius,
                                                     projection,
                                                     angle)

        x_min = min(max(math.floor(x_min), 0), length_image - 1)
        x_max = min(max(math.ceil(x_max), 0), length_image - 1)
        y_min = min(max(math.floor(y_min), 0), height_image - 1)
        y_max = min(max(math.ceil(y_max), 0), height_image - 1)

        img[y_min:y_max + 1, x_min:x_max + 1] = 255

    return img


def reconstruction_3d(images, projection, radius,
                      origin_point=(0.0, 0.0, 0.0),
                      points_3d=None,
                      verbose=False):

    if len(images) == 0:
        return

    origin_radius = 2048 * 2

    if points_3d is None:
        points_3d = collections.deque()
        points_3d.append(origin_point)

    nb_iteration = 0

    while radius < origin_radius:
        radius *= 2.0
        nb_iteration += 1

    for i in range(nb_iteration):

        if len(images) == 1:
            points_3d = split_points_3d_plan(points_3d, radius)
        else:
            points_3d = split_points_3d(points_3d, radius)

        radius /= 2.0

        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration, ' : ', len(points_3d),

        points_3d = octree_builder(
            images, points_3d, radius, projection)

        if verbose is True:
            print ' - ', len(points_3d)

    return points_3d


def build_groups(images, points_3d, index_image, projection, radius):
    height_image, length_image = numpy.shape(images.itervalues().next())

    import time

    # angle_selected = range(0, 360, 30)
    angle_selected = [120, 0]

    start = time.time()
    groups = dict()
    for angle in angle_selected:
        for i in xrange(len(index_image[angle][0])):
            x, y = (index_image[angle][0][i], index_image[angle][1][i])
            groups[(angle, x, y)] = [list(), 0, angle]

    print "Time : ", time.time() - start
    start = time.time()

    new_points_3d = collections.deque()
    while True:
        try:
            pt3d = points_3d.popleft()
            list_group = list()
            stats = 0

            new_point = [pt3d, list_group, stats]
            new_points_3d.append(new_point)

            for angle in angle_selected:
                x_min, x_max, y_min, y_max = bbox_projection(
                    pt3d, radius, projection, angle)

                x_min = min(max(math.floor(x_min), 0), length_image - 1)
                x_max = min(max(math.ceil(x_max), 0), length_image - 1)
                y_min = min(max(math.floor(y_min), 0), height_image - 1)
                y_max = min(max(math.ceil(y_max), 0), height_image - 1)

                img = images[angle][y_min:y_max + 1, x_min:x_max + 1]
                index = numpy.where(img > 0)

                for i in xrange(len(index[0])):
                    x, y = (index[0][i] + y_min, index[1][i] + x_min)

                    groups[(angle, x, y)][0].append(new_point)
                    # groups[(angle, x, y)][1] = len(groups[(angle, x, y)][0])
                    list_group.append(groups[(angle, x, y)])

        except IndexError:
            break

    for key in groups:
        groups[key][1] = len(groups[key][0])

    print "Time : ", time.time() - start

    return new_points_3d, groups


def octree_builder_2(images, pts, groups, radius, projection):
    kept = collections.deque()

    height_image, length_image = numpy.shape(images.itervalues().next())

    error_tolerance = len(images)
    if len(images) >= 10:
        error_tolerance = 0

    acceptation_criteria = len(images) - error_tolerance

    while True:
        try:
            point, point_group, stats = pts.popleft()

            for angle in images:
                if point_3d_is_in_image(images[angle],
                                        height_image,
                                        length_image,
                                        point,
                                        projection,
                                        angle,
                                        radius):
                    stats += 1

            if stats >= acceptation_criteria:
                kept.append(point)
            else:
                for g in point_group:
                    g[1] -= 1

        except IndexError:
            break

    inf = float('inf')
    for key in groups:
        group, nb, angle = groups[key]
        if nb <= 0:
            min_dist = inf
            save_pt = list()
            for pt3D, list_group, sum_dist in group:
                if sum_dist < min_dist:
                    min_dist = sum_dist
                    save_pt = list()
                    save_pt.append((pt3D, list_group))
                elif sum_dist == min_dist:
                    save_pt.append((pt3D, list_group))

            save_for_sure_pt = list()
            for pt3d, list_group in save_pt:
                for pts_2, nb_2, angle_2 in list_group:
                    if nb_2 <= 0 and angle != angle_2:
                        save_for_sure_pt.append(pt3d)

            if save_for_sure_pt:
                for pt3d in save_for_sure_pt:
                    kept.append(pt3d)
            else:
                for pt3d, list_group in save_pt:
                    kept.append(pt3d)

    return collections.deque(set(kept))


def reconstruction_3d_2(images, angle_ref, projection, radius,
                        origin_point=(0.0, 0.0, 0.0),
                        points_3d=None,
                        verbose=False):

    if len(images) == 0:
        return

    origin_radius = 2048 * 2

    if points_3d is None:
        points_3d = collections.deque()
        points_3d.append(origin_point)

    nb_iteration = 0
    while radius < origin_radius:
        radius *= 2.0
        nb_iteration += 1

    index_image = dict()
    for angle in images:
        index_image[angle] = numpy.where(images[angle] > 0)

    for i in range(nb_iteration):

        if len(images) == 1:
            points_3d = split_points_3d_plan(points_3d, radius)
        else:
            points_3d = split_points_3d(points_3d, radius)

        radius /= 2.0

        # ======================================================================

        pts, groups = build_groups(images,
                                   points_3d,
                                   index_image,
                                   projection,
                                   radius)

        # ======================================================================

        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration, ' : ', len(pts),

        points_3d = octree_builder_2(
            images, pts, groups, radius, projection)

        if verbose is True:
            print ' - ', len(points_3d)

    return points_3d
