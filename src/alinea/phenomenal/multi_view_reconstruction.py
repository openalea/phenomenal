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


def octree_builder(images, points, radius, projection, error_tolerance):
    kept = collections.deque()

    height_image, length_image = numpy.shape(images.itervalues().next())

    while True:
        try:
            point = points.popleft()

            negative_weight = 0
            for angle in images:
                if not point_3d_is_in_image(images[angle],
                                            height_image,
                                            length_image,
                                            point,
                                            projection,
                                            angle,
                                            radius):
                    negative_weight += 1
                    if negative_weight > error_tolerance:
                        break

            if negative_weight <= error_tolerance:
                kept.append(point)

        except IndexError:
            break

    return kept


def reconstruction_3d(images, projection, radius,
                      error_tolerance=0,
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
            images, points_3d, radius, projection, error_tolerance)

        if verbose is True:
            print ' - ', len(points_3d)

    return points_3d


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

# ==============================================================================


def create_groups(images, angles_ref):
    groups = dict()
    for angle in angles_ref:
        index = numpy.where(images[angle] > 0)
        for i in xrange(len(index[0])):
            x, y = (index[0][i], index[1][i])
            groups[(angle, x, y)] = [list(), 0, angle]

    return groups


def fill_groups(images, points_3d, groups, projection, radius, angles_ref):
    height_image, length_image = numpy.shape(images.itervalues().next())

    # ==========================================================================
    # Clear groups
    for key in groups:
        groups[key][0] = list()
        groups[key][1] = 0

    new_points_3d = collections.deque()
    while True:
        try:
            pt3d = points_3d.popleft()

            list_group = list()
            stats = 0

            new_point = [pt3d, list_group, stats]
            new_points_3d.append(new_point)

            for angle in angles_ref:
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
                    list_group.append(groups[(angle, x, y)])

        except IndexError:
            break

    for key in groups:
        groups[key][1] = len(groups[key][0])

    return new_points_3d, groups


def kept_points_3d(images, pts, radius, projection, error_tolerance):

    kept = collections.deque()
    height_image, length_image = numpy.shape(images.itervalues().next())
    acceptation_criteria = len(images) - error_tolerance
    weight_points = dict()

    while True:
        try:
            point, groups, weight = pts.popleft()

            for angle in images:
                if point_3d_is_in_image(images[angle],
                                        height_image,
                                        length_image,
                                        point,
                                        projection,
                                        angle,
                                        radius):
                    weight += 1

            if weight >= acceptation_criteria:
                kept.append(point)
            else:
                for group in groups:
                    group[1] -= 1

            weight_points[point] = weight

        except IndexError:
            break

    return kept, weight_points


def compute_sum_weight_of_neighbort(point,
                                    weight_points,
                                    radius,
                                    distance_to_neighbort):

    weight = 0
    diameter = radius * 2
    x, y, z = point
    range_neighbort = list()

    for i in range(-distance_to_neighbort, distance_to_neighbort, 1):
        range_neighbort.append(i * diameter)

    for i in range_neighbort:
        for j in range_neighbort:
            for k in range_neighbort:
                pt = (x + i, y + j, z + k)
                if pt in weight_points:
                    if weight_points[pt] == 12:
                        weight += 312
                    weight += weight_points[pt]

    return weight


def compute_list_max_weight(group):

    max_weight = 0
    list_max_weight = list()

    for pt3D, list_group, weight in group:
        if weight > max_weight:
            max_weight = weight
            save_pt = list()
            save_pt.append((pt3D, list_group, weight))
        elif weight == max_weight:
            list_max_weight.append((pt3D, list_group, weight))

    return list_max_weight


def compute_list_different_angle(list_max_weight, angle):

    list_different_angle = list()

    for pt3d, list_group, weight in list_max_weight:
        for pts_2, nb_2, angle_2 in list_group:
            if nb_2 <= 0 and angle != angle_2:
                list_different_angle.append(pt3d)

    return list_different_angle


def compute_list_max_neighbort_weigh(list_max_weight,
                                     weight_points,
                                     radius,
                                     distance_to_neighbort):
    max_sum_weight = 0
    list_max_neighbort_weigh = list()
    for pt3d, list_group, weight in list_max_weight:

        sum_weight_of_neighbort = compute_sum_weight_of_neighbort(
            pt3d, weight_points, radius, distance_to_neighbort)

        if sum_weight_of_neighbort > max_sum_weight:
            max_sum_weight = sum_weight_of_neighbort
            list_max_neighbort_weigh = list()
            list_max_neighbort_weigh.append(pt3d)

        if sum_weight_of_neighbort == max_sum_weight:
            list_max_neighbort_weigh.append(pt3d)

    return list_max_neighbort_weigh


def check_groups(kept, groups, weight_points, radius, distance_to_neighbort=2):

    for key in groups:
        group, nb, angle = groups[key]
        if nb <= 0:

            list_max_weight = compute_list_max_weight(group)

            list_different_angle = compute_list_different_angle(
                list_max_weight, angle)

            if list_different_angle:
                for pt3d in list_different_angle:
                    kept.append(pt3d)
            else:

                list_max_neighbort_weigh = compute_list_max_neighbort_weigh(
                    list_max_weight,
                    weight_points,
                    radius,
                    distance_to_neighbort)

                for pt3d in list_max_neighbort_weigh:
                    kept.append(pt3d)

    return collections.deque(set(kept))


def new_reconstruction_3d(images, projection, radius, angles_ref,
                          error_tolerance=0,
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

    # ==========================================================================
    # Create Groups
    groups = create_groups(images, angles_ref)

    # ==========================================================================

    for i in range(nb_iteration):

        if len(images) == 1:
            points_3d = split_points_3d_plan(points_3d, radius)
        else:
            points_3d = split_points_3d(points_3d, radius)

        radius /= 2.0

        # ======================================================================

        pts, groups = fill_groups(
            images, points_3d, groups, projection, radius, angles_ref)

        # ======================================================================

        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration, ' : ', len(pts),

        # ======================================================================

        points_3d, weight_points = kept_points_3d(
            images, pts, radius, projection, error_tolerance)

        points_3d = check_groups(points_3d, groups, weight_points, radius)

        # ======================================================================

        if verbose is True:
            print ' - ', len(points_3d)

    return points_3d
