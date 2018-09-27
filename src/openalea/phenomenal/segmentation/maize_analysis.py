# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import print_function, absolute_import

import numpy
import math
import scipy.integrate

from .plane_interception import (intercept_points_along_path_with_planes,
                                 max_distance_in_points)
# ==============================================================================


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / numpy.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::
        0 and between 2pi

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return numpy.arccos(numpy.clip(numpy.dot(v1_u, v2_u), -1.0, 1.0))


def get_max_distance(node, nodes):
    max_distance = 0
    max_node = node

    for n in nodes:
        distance = abs(numpy.linalg.norm(numpy.array(node) - numpy.array(n)))
        if distance >= max_distance:
            max_distance = distance
            max_node = n

    return max_node, max_distance


def compute_width_organ(closest_nodes):

    width = list()
    for nodes in closest_nodes:
        width.append(max_distance_in_points(nodes))

    return width


def compute_curvilinear_abscissa(polyline, length):

    v = 0.0
    curvilinear_abscissa = [0]
    for n1, n2 in zip(polyline, polyline[1:]):
        v += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))
        curvilinear_abscissa.append(v / float(length))

    return curvilinear_abscissa


def compute_length_organ(polyline):

    length = 0
    for n1, n2 in zip(polyline, polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    return length


def compute_inclination_angle(polyline, step=1):

    if not len(polyline) > step:
        return None

    length = 0
    for (x0, y0, z0), (x1, y1, z1) in zip(polyline[::step],
                                          polyline[step::step]):
        length += numpy.linalg.norm(numpy.array((x1 - x0, y1 - y0, z1 - z0)))

    angles = list()
    z_axis = numpy.array([0, 0, 1])

    for (x0, y0, z0), (x1, y1, z1) in zip(polyline[::step],
                                          polyline[step::step]):
        vector = numpy.array((x1 - x0, y1 - y0, z1 - z0))
        norm = numpy.linalg.norm(vector)
        angle = angle_between(z_axis, vector)
        angles.append(math.degrees(angle) * (norm / length))

    inclination_angle = sum(angles) / float(len(angles))

    if inclination_angle > 180.0:
        inclination_angle -= 360.0
    return inclination_angle


def compute_fitted_width(width, curvilinear_abscissa):

    x = numpy.array(curvilinear_abscissa)
    XX = numpy.vstack((x ** 2, x)).T
    p_all = numpy.linalg.lstsq(XX, width[::-1])[0]
    fitted_width = numpy.dot(p_all, XX.T)

    return fitted_width


def compute_vector_mean(polyline):

    x, y, z = polyline[0]

    vectors = list()
    for i in range(1, len(polyline)):
        xx, yy, zz = polyline[i]

        v = (xx - x, yy - y, zz - z)
        vectors.append(v)

    vector_mean = numpy.array(vectors).mean(axis=0)

    return vector_mean


def compute_azimuth_angle(polyline):

    vector_mean = compute_vector_mean(polyline)
    x, y, z = vector_mean
    azimuth_angle = math.degrees(math.atan2(y, x))

    return azimuth_angle, tuple(vector_mean)


def compute_insertion_angle(polyline, stem_vector_mean):

    x, y, z = polyline[0]

    vectors = list()
    for i in range(1, len(polyline) / 4 + 1):
        xx, yy, zz = polyline[i]
        vectors.append((xx - x, yy - y, zz - z))

    insertion_vector = numpy.array(vectors).mean(axis=0)
    insertion_angle = angle_between(insertion_vector, stem_vector_mean)
    insertion_angle = math.degrees(insertion_angle)

    if insertion_angle > 180.0:
        insertion_angle -= 360.0

    return insertion_angle, tuple(insertion_vector)


# ==============================================================================
# ==============================================================================
# ==============================================================================


def organ_analysis(organ, polyline, closest_nodes, stem_vector_mean=None):

    if len(polyline) <= 1:
        return None

    organ.info['pm_position_tip'] = tuple(polyline[-1])
    organ.info['pm_position_base'] = tuple(polyline[0])
    organ.info['pm_z_tip'] = polyline[-1][2]
    organ.info['pm_z_base'] = polyline[0][2]

    length = compute_length_organ(polyline)
    organ.info['pm_length'] = length
    normalized_curvilinear_abscissa = compute_curvilinear_abscissa(
        polyline, length)
    curvilinear_abscissa = compute_curvilinear_abscissa(polyline, 1)
    # Compute width
    width = compute_width_organ(closest_nodes)

    organ.info['pm_width_max'] = max(width)
    organ.info['pm_width_mean'] = sum(width) / float(len(width))
    organ.info['pm_surface'] = scipy.integrate.simps(
        width, curvilinear_abscissa)

    fitted_width = compute_fitted_width(width, normalized_curvilinear_abscissa)
    organ.info['pm_fitted_width_max'] = max(fitted_width)
    organ.info['pm_fitted_width_mean'] = (sum(fitted_width) /float(len(
        fitted_width)))
    organ.info['pm_fitted_surface'] = scipy.integrate.simps(
        fitted_width, curvilinear_abscissa)
    # Compute azimuth
    azimuth_angle, vector_mean = compute_azimuth_angle(polyline)
    organ.info['pm_vector_mean'] = vector_mean
    organ.info['pm_azimuth_angle'] = azimuth_angle

    inclination_angle = compute_inclination_angle(polyline)
    organ.info['pm_inclination_angle'] = inclination_angle

    if stem_vector_mean is not None and len(polyline) >= 4:
        insertion_angle, vector = compute_insertion_angle(
            polyline, stem_vector_mean)

        organ.info['pm_insertion_angle_vector'] = vector
        organ.info['pm_insertion_angle'] = insertion_angle

    return organ


def maize_stem_analysis(vo, voxels_size, distance_plane=0.75):

    voxels_position = vo.voxels_position()
    polyline = vo.get_longest_segment().polyline

    if len(polyline) <= 1:
        return vo

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes, _ = intercept_points_along_path_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        distance_from_plane=distance_plane * voxels_size,
        without_connection=True,
        voxels_size=voxels_size)

    # ==========================================================================

    return organ_analysis(vo, polyline, closest_nodes)


def maize_mature_leaf_analysis(vo, voxels_size,
                               stem_vector_mean,
                               distance_plane=0.75):

    voxels_position = vo.voxels_position()
    polyline = vo.get_longest_segment().polyline

    if len(polyline) <= 3:
        return None

    vo.info['pm_full_length'] = compute_length_organ(polyline)

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes, _ = intercept_points_along_path_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        distance_from_plane=distance_plane * voxels_size,
        voxels_size=voxels_size)

    # ==========================================================================
    # Compute extremity
    index_position_base = vo.get_real_index_position_base()

    # ==========================================================================

    real_polyline = polyline[index_position_base:]
    real_closest_nodes = closest_nodes[index_position_base:]

    vo = organ_analysis(vo,
                        real_polyline,
                        real_closest_nodes,
                        stem_vector_mean)

    return vo


def maize_growing_leaf_analysis_real_length(maize_segmented, vo):

    voxels = maize_segmented.get_voxels_position(except_organs=[vo])
    longest_polyline = vo.get_longest_segment().polyline
    voxels = set(voxels).intersection(longest_polyline)
    z = numpy.max(numpy.array(list(voxels))[:, 2])
    return z


def maize_growing_leaf_analysis(vo, voxels_size,
                                stem_vector_mean,
                                voxels,
                                distance_plane=0.75):

    voxels_position = vo.voxels_position()
    polyline = vo.get_longest_segment().polyline
    vo.info['pm_full_length'] = compute_length_organ(polyline)

    if len(polyline) <= 1:
        return vo

    real_longest_polyline = vo.real_longest_polyline()
    vo.info['pm_length_with_speudo_stem'] = compute_length_organ(
        real_longest_polyline)

    # ==========================================================================
    # Compute height of the leaf
    closest_nodes, _ = intercept_points_along_path_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        distance_from_plane=distance_plane * voxels_size,
        voxels_size=voxels_size)

    # ==========================================================================
    # Compute extremity
    voxels = list(set(polyline).intersection(set(voxels)))

    index_position_base = 0
    for i, node in enumerate(polyline):
        if node in voxels:
            index_position_base = i

    real_polyline = polyline[index_position_base:]
    real_closest_nodes = closest_nodes[index_position_base:]

    vo = organ_analysis(vo, real_polyline, real_closest_nodes,
                        stem_vector_mean)

    if vo is not None:
        vo.info['pm_length_speudo_stem'] = (
            vo.info['pm_length_with_speudo_stem'] - vo.info['pm_length'])

    return vo


def maize_analysis(maize_segmented):
    """ Update info fiel of the VoxelSegmentation object with the analysis
    result computed. Each organ are a specific algorithm to extract information.

    Parameters
    ----------
    maize_segmented : VoxelSegmentation

    Returns
    -------
    maize_segmented: VoxelSegmentation
    """

    voxels_size = maize_segmented.voxels_size
    for vo in maize_segmented.voxel_organs:
        vo.info = dict()
        vo.info['pm_label'] = vo.label
        vo.info['pm_sub_label'] = vo.sub_label
        vo.info['pm_voxels_volume'] = (
            len(vo.voxels_position()) * maize_segmented.voxels_size ** 3)

    # ==========================================================================

    vo_stem = maize_segmented.get_stem()
    vo_stem = maize_stem_analysis(vo_stem, voxels_size)

    # ==========================================================================

    mature_leafs = list()
    for vo_mature_leaf in maize_segmented.get_mature_leafs():

        vo_mature_leaf = maize_mature_leaf_analysis(
            vo_mature_leaf, voxels_size, vo_stem.info['pm_vector_mean'])

        if vo_mature_leaf is None:
            continue

        mature_leafs.append((vo_mature_leaf, vo_mature_leaf.info["pm_z_base"]))
    mature_leafs.sort(key=lambda x: x[1])

    # ==========================================================================

    growing_leafs = list()
    for vo_growing_leaf in maize_segmented.get_growing_leafs():

        z = maize_growing_leaf_analysis_real_length(maize_segmented,
                                                    vo_growing_leaf)
        growing_leafs.append((vo_growing_leaf, z))
    growing_leafs.sort(key=lambda x: x[1])

    voxels = vo_stem.voxels_position()
    for vo, _ in growing_leafs:
        # TODO : bug here when two leaf are connected by the tips, the length is directly 0
        vo = maize_growing_leaf_analysis(
            vo, voxels_size, vo_stem.info['pm_vector_mean'], voxels)

        if vo is None:
            continue

        voxels = voxels.union(vo.voxels_position())

    # ==========================================================================

    for leaf_number, (vo, _) in enumerate(mature_leafs + growing_leafs):
        vo.info["pm_leaf_number"] = leaf_number + 1

    maize_segmented.update_plant_info()

    return maize_segmented
