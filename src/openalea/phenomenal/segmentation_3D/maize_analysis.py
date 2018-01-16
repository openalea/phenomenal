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
import numpy
import math

from openalea.phenomenal.segmentation_3D import (
    intercept_points_along_path_with_planes,
    max_distance_in_points)

# ==============================================================================


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / numpy.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

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


def compute_width_organ(organ, closest_nodes):

    width = list()
    for nodes in closest_nodes:
        width.append(max_distance_in_points(nodes))

    organ.info['width_max'] = max(width)
    organ.info['width_mean'] = sum(width) / float(len(width))

    return organ


def compute_length_organ(organ, polyline):

    length = 0
    for n1, n2 in zip(polyline, polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    organ.info['length'] = length

    return organ


def compute_azimuth_vector_mean_organ(organ, polyline):

    if len(polyline) > 1:
        x, y, z = polyline[0]

        vectors = list()
        for i in range(1, len(polyline)):
            xx, yy, zz = polyline[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)
        organ.info['vector_mean'] = tuple(vector_mean)

        x, y, z = vector_mean
        angle = math.atan2(y, x)
        angle = angle + 2 * math.pi if angle < 0 else angle
        organ.info['azimuth'] = angle

    return organ


def compute_angle(organ, polyline, stem_vector_mean):

    if len(polyline) > 3:

        x, y, z = polyline[0]

        vectors = list()
        for i in range(1, len(polyline) / 4 + 1):
            xx, yy, zz = polyline[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)

        organ.info['vector_mean_one_quarter'] = tuple(vector_mean)
        organ.info['angle'] = angle_between(vector_mean, stem_vector_mean)

    return organ


def organ_analysis(organ, polyline, closest_nodes, stem_vector_mean=None):

    if len(polyline) <= 1:
        return organ

    organ.info['position_tip'] = tuple(polyline[-1])
    organ.info['position_base'] = tuple(polyline[0])
    organ.info['z_tip'] = polyline[-1][2]
    organ.info['z_base'] = polyline[0][2]

    # Compute width
    organ = compute_width_organ(organ, closest_nodes)

    # Compute length
    organ = compute_length_organ(organ, polyline)

    # Compute azimuth
    organ = compute_azimuth_vector_mean_organ(organ, polyline)

    if organ.label == "mature_leaf" or organ.label == "cornet_leaf":
        # ======================================================================
        # Compute intersection
        organ.info["position_intersection"] = polyline[0]
        organ.info["z_intersection"] = polyline[0][2]

        # ======================================================================
        # Compute angle
        organ = compute_angle(organ, polyline, stem_vector_mean)

    return organ


def maize_stem_analysis(stem_voxel_organ, distance_plane=0.75):

    voxels_position = stem_voxel_organ.voxels_position()
    voxels_size = stem_voxel_organ.info['voxels_size']
    polyline = stem_voxel_organ.longest_polyline()

    if len(polyline) <= 1:
        return stem_voxel_organ
    # ==========================================================================
    # Compute height of the leaf

    closest_nodes, _ = intercept_points_along_path_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        distance_from_plane=distance_plane * voxels_size,
        without_connection=True,
        voxels_size=voxels_size)

    # ==========================================================================
    # Compute extremity
    index_position_base = 0
    # ==========================================================================

    real_polyline = polyline[index_position_base:]
    real_closest_nodes = closest_nodes[index_position_base:]

    stem_voxel_organ = organ_analysis(stem_voxel_organ,
                                      real_polyline,
                                      real_closest_nodes)

    return stem_voxel_organ


def maize_mature_leaf_analysis(mature_leaf_voxel_organ,
                               stem_vector_mean,
                               distance_plane=0.75):

    voxels_position = mature_leaf_voxel_organ.voxels_position()
    voxels_size = mature_leaf_voxel_organ.info['voxels_size']
    polyline = mature_leaf_voxel_organ.longest_polyline()

    # ==========================================================================

    if len(polyline) <= 1:
        return mature_leaf_voxel_organ

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes, _ = intercept_points_along_path_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        distance_from_plane=distance_plane * voxels_size,
        voxels_size=voxels_size)

    # ==========================================================================
    # Compute extremity
    index_position_base = len(polyline) - 1
    for i in range(len(polyline) - 1, -1, -1):
        if polyline[i] not in set(voxels_position):
            index_position_base = i
            break

    # for i, (nodes, node) in enumerate(zip(closest_nodes, polyline)):
    #     if len(nodes) > 0 and node in set(nodes):
    #         index_position_base = i
    #         break

    # ==========================================================================

    real_polyline = polyline[index_position_base:]
    real_closest_nodes = closest_nodes[index_position_base:]

    mature_leaf_voxel_organ = organ_analysis(mature_leaf_voxel_organ,
                                             real_polyline,
                                             real_closest_nodes,
                                             stem_vector_mean)

    return mature_leaf_voxel_organ


def maize_cornet_leaf_analysis_real_length(organ, voxels):

    real_longest_polyline = organ.real_longest_polyline()

    if len(real_longest_polyline) <= 1:
        return organ

    length = 0
    for n1, n2 in zip(real_longest_polyline, real_longest_polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))
    organ.info['not_visible_length'] = length

    longest_polyline = organ.longest_polyline()
    voxels = set(voxels).intersection(longest_polyline)
    z = numpy.max(numpy.array(list(voxels))[:, 2])
    organ.info["z_intersection"] = z

    return organ


def maize_cornet_leaf_analysis(organ,
                               stem_vector_mean,
                               voxels,
                               distance_plane=0.75):

    voxels_position = organ.voxels_position()
    voxels_size = organ.info['voxels_size']
    polyline = organ.longest_polyline()

    if len(polyline) <= 1:
        return organ

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

    organ = organ_analysis(organ, real_polyline, real_closest_nodes,
                           stem_vector_mean)

    return organ


def get_highest_organ(voxel_organs):

    z_max = float("-inf")
    highest_voxel_organ = None
    for voxel_organ in voxel_organs:
        for voxel_segment in voxel_organ.voxel_segments:
            if len(voxel_segment.polyline) > 0:
                z = numpy.max(numpy.array(voxel_segment.polyline)[-1, 2])

                if z > z_max:
                    z_max = z
                    highest_voxel_organ = voxel_organ

    return highest_voxel_organ


def maize_analysis(voxel_maize_segmentation):

    for vo in voxel_maize_segmentation.voxel_organs:
        vo.info['label'] = vo.label
        vo.info['voxels_size'] = voxel_maize_segmentation.voxels_size
        vo.info['voxels_number'] = len(vo.voxels_position())

    vo_stem = voxel_maize_segmentation.get_stem()
    vo_stem = maize_stem_analysis(vo_stem)

    lorder = list()
    for vo_mature_leaf in voxel_maize_segmentation.get_mature_leafs():
        vo_mature_leaf = maize_mature_leaf_analysis(
            vo_mature_leaf, vo_stem.info['vector_mean'])

        lorder.append((vo_mature_leaf, vo_mature_leaf.info["z_intersection"]))

    lorder.sort(key=lambda x: x[1])

    num_order = 1
    for vo, _ in lorder:
        vo.info["order"] = num_order
        num_order += 1

    lorder = list()
    for vo_cornet_leaf in voxel_maize_segmentation.get_cornet_leafs():

        voxels = voxel_maize_segmentation.get_voxels_position(
            except_organs=[vo_cornet_leaf])

        vo_cornet_leaf = maize_cornet_leaf_analysis_real_length(
            vo_cornet_leaf, voxels)

        lorder.append((vo_cornet_leaf,
                       vo_cornet_leaf.info["z_intersection"]))

    voxels = set(vo_stem.voxels_position())
    lorder.sort(key=lambda x: x[1])
    for vo, _ in lorder:
        vo.info["order"] = num_order
        num_order += 1

        # TODO : bug here when two leaf are connected by the tips, the length  is directly 0

        vo = maize_cornet_leaf_analysis(
            vo, vo_stem.info['vector_mean'], voxels)

        voxels = voxels.union(set(vo.voxels_position()))

    return voxel_maize_segmentation
