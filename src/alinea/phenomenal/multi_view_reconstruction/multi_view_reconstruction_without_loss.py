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
import collections
import math
import numpy
import time
import scipy.spatial

from alinea.phenomenal.multi_view_reconstruction.multi_view_reconstruction \
    import (split_voxel_centers_in_four,
            split_voxel_centers_in_eight,
            get_bounding_box_voxel_projected,
            voxel_is_visible_in_image)
# ==============================================================================


def create_groups(images_projections_refs):
    groups = dict()

    group_id = 0
    for image, projection, ref in images_projections_refs:
        if ref is True:
            xx, yy = numpy.where(image > 0)
            for x, y in zip(xx, yy):
                groups[(group_id, x, y)] = [list(), 0, group_id]

        group_id += 1

    return groups


def fill_groups(images_projections_refs, groups, voxel_centers, voxel_size):

    # ==========================================================================
    # Clear groups
    for key in groups:
        groups[key][0] = list()
        groups[key][1] = 0

    weight_points = collections.defaultdict(int)

    # groups = collections.defaultdict(list)
    kept = collections.deque()
    for voxel_center in voxel_centers:
        list_group = list()
        stats = 0

        new_point = [voxel_center, list_group, stats]
        kept.append(new_point)

        group_id = 0
        for image, projection, ref in images_projections_refs:
            if ref is True:

                height_image, length_image = image.shape

                x_min, x_max, y_min, y_max = get_bounding_box_voxel_projected(
                    voxel_center, voxel_size, projection)

                x_min = int(min(max(math.floor(x_min), 0), length_image - 1))
                x_max = int(min(max(math.ceil(x_max), 0), length_image - 1))
                y_min = int(min(max(math.floor(y_min), 0), height_image - 1))
                y_max = int(min(max(math.ceil(y_max), 0), height_image - 1))

                img = image[y_min:y_max + 1, x_min:x_max + 1]

                xx, yy = numpy.where(img > 0)

                xx += y_min
                yy += x_min

                # b = g[y_min:y_max + 1, x_min:x_max + 1]
                # for index, value in numpy.ndenumerate(b):
                #     b[index] = value.append(voxel_center)

                for x, y in zip(xx, yy):
                    groups[(group_id, x, y)][0].append(new_point)
                    list_group.append(groups[(group_id, x, y)])

                if numpy.any(img > 0):
                    weight_points[voxel_center] += 1

            else:
                if voxel_is_visible_in_image(
                        voxel_center, voxel_size, image, projection):
                    weight_points[voxel_center] += 1

            group_id += 1

    for key in groups:
        groups[key][1] = len(groups[key][0])

    return kept, groups, weight_points


def kept_points_3d(acceptation_criteria, pts, weight_points):

    kept = collections.deque()
    for voxel_center, groups, weight in pts:

        weight = weight_points[voxel_center]

        if weight >= acceptation_criteria:
            kept.append(voxel_center)
        else:
            for group in groups:
                group[1] -= 1

    return kept


def compute_sum_weight_of_neighbor(point,
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


def compute_list_max_weight(group, weight_points):

    max_weight = 0
    for pt3D, list_group, _ in group:
        weight = weight_points[pt3D]

        if weight > max_weight:
            max_weight = weight

    list_max_weight = list()
    for pt3D, list_group, _ in group:
        weight = weight_points[pt3D]

        if weight == max_weight:
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

        sum_weight_of_neighbort = compute_sum_weight_of_neighbor(
            pt3d, weight_points, radius, distance_to_neighbort)

        if sum_weight_of_neighbort > max_sum_weight:
            max_sum_weight = sum_weight_of_neighbort
            list_max_neighbort_weigh = list()
            list_max_neighbort_weigh.append(pt3d)

        if sum_weight_of_neighbort == max_sum_weight:
            list_max_neighbort_weigh.append(pt3d)

    return list_max_neighbort_weigh


def check_groups(kept, groups, weight_points, voxel_size,
                 distance_to_neighbort=2):

    for key in groups:
        group, nb, angle = groups[key]
        if nb <= 0 and len(group) > 0:

            # list_max_weight = compute_list_max_weight(group, weight_points)

            nodes_src = list()
            for pt3d, list_group, weight in group:
                nodes_src.append(pt3d)

            # nodes_src = numpy.array(nodes_src)
            k = numpy.array(kept)

            result = scipy.spatial.distance.cdist(nodes_src, k, 'euclidean')

            min1 = result.min(axis=1)
            # m = min1.min(axis=0)

            # dst_index = numpy.argmin(result, axis=1)
            src_index = numpy.argmin(min1, axis=0)

            pt3d = nodes_src[src_index]
            kept.append(pt3d)

                # pt2 = nodes[dst_index[src_index]]

                # nodes_dst = nodes

            # list_different_angle = compute_list_different_angle(
            #     list_max_weight, angle)
            #
            # if list_different_angle:
            #     kept += list_different_angle
            # else:

                # list_max_neighbort_weigh = compute_list_max_neighbort_weigh(
                #     list_max_weight,
                #     weight_points,
                #     voxel_size,
                #     distance_to_neighbort)

                # kept += list_max_neighbort_weigh

            # for pt3d, list_group, weight in list_max_weight:
            #     kept.append(pt3d)

    return collections.deque(set(kept))


def reconstruction_without_loss(images_projections_refs,
                                voxel_size=4,
                                error_tolerance=0,
                                voxel_center_origin=(0.0, 0.0, 0.0),
                                world_size=4096,
                                voxel_centers=None,
                                verbose=False):

    if len(images_projections_refs) == 0:
        return

    if voxel_centers is None:
        voxel_centers = collections.deque()
        voxel_centers.append(voxel_center_origin)

    nb_iteration = 0
    while voxel_size < world_size:
        voxel_size *= 2.0
        nb_iteration += 1

    # ==========================================================================
    # Create Groups

    t0 = time.time()
    groups = create_groups(images_projections_refs)
    print "Time create groups", time.time() - t0
    t0 = time.time()
    # ==========================================================================

    for i in range(nb_iteration):
        if verbose is True:
            print 'Iteration', i + 1, '/', nb_iteration
            # print ' : ', len(voxel_centers),

        if len(images_projections_refs) == 1:
            voxel_centers = split_voxel_centers_in_four(voxel_centers,
                                                        voxel_size)
        else:
            voxel_centers = split_voxel_centers_in_eight(voxel_centers,
                                                         voxel_size)
        voxel_size /= 2.0
        print "Time split_voxel", time.time() - t0
        t0 = time.time()
        # ======================================================================

        voxel_centers, groups, weight_points = fill_groups(
            images_projections_refs, groups, voxel_centers, voxel_size)
        print "Time fill groups", time.time() - t0
        t0 = time.time()

        # ======================================================================

        acceptation_criteria = len(images_projections_refs) - error_tolerance
        voxel_centers = kept_points_3d(
            acceptation_criteria, voxel_centers, weight_points)

        print "Time kept_points_3d", time.time() - t0
        t0 = time.time()
        voxel_centers = check_groups(voxel_centers, groups, weight_points, voxel_size)

        print "Time check_groups", time.time() - t0
        t0 = time.time()
        # ======================================================================

        # if verbose is True:
            # print ' - ', len(voxel_centers)

    return voxel_centers
