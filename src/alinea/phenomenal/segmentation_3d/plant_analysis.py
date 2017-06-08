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
import scipy.interpolate
import math
import scipy.spatial

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes_with_planes)

from alinea.phenomenal.segmentation_3d.algorithm import get_length_point_cloud
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


def voxels_path_analysis(voxels_position, path, voxel_size,
                         higher_path, all_vs, distance_plane=0.50):

    info = dict()

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        all_vs,
        path,
        radius=8,
        dist=distance_plane * voxel_size)

    voxels = set().union(*closest_nodes)
    voxels = list(voxels.intersection(set(higher_path)))
    z = numpy.max(numpy.array(voxels)[:, 2])

    info["z_intersection"] = z

    # ==========================================================================
    # Compute nodes along the path

    set_voxel = set(list(voxels_position))
    closest_nodes = [list(set_voxel.intersection(set(nodes))) for nodes in
                     closest_nodes]

    # ==========================================================================
    # Compute the new leaf

    tmp_closest_nodes = list()
    tmp_path = list()

    for nodes, node in zip(closest_nodes, path):
        if len(nodes) > 0 and node in set(nodes):
            tmp_closest_nodes.append(nodes)
            tmp_path.append(node)

    path = tmp_path
    closest_nodes = tmp_closest_nodes

    # centred_path = [tuple(numpy.array(nodes).mean(axis=0)) for nodes in
    #                 closest_nodes]
    #
    # seen = set()
    # seen_add = seen.add
    # centred_path = [numpy.array(x) for x in centred_path if not (
    #     x in seen or seen_add(x))]
    #
    # # centred_path = path
    # arr_centred_path = numpy.array(centred_path, dtype=float).transpose()
    #
    # k = 5
    # while len(centred_path) <= k and k > 1:
    #     k -= 1
    #
    # tck, u = scipy.interpolate.splprep(arr_centred_path, k=k)
    # xxx, yyy, zzz = scipy.interpolate.splev(
    #     numpy.linspace(0, 1, len(centred_path)), tck)

    # real_path = [(x, y, z) for x, y, z in zip(xxx, yyy, zzz)]

    # real_path = list()
    # for i in range(len(xxx)):
    #     real_path.append((int(xxx[i]), int(yyy[i]), int(zzz[i])))

    # print len_index_path, len(centred_path), len(real_path)
    # show_list_points_3d([path, centred_path],
    #                     list_color=[(1, 0, 0), (0, 1, 0)])

    # info['polyline'] = path

    # from alinea.phenomenal.display.segmentation3d import show_list_points_3d
    # show_list_points_3d([voxel, path], list_color=[(0, 1, 0), (1, 0, 0)])

    # path = real_path
    # ==========================================================================

    # planes, closest_nodes = compute_closest_nodes(
    #     arr_voxel,
    #     path,
    #     radius=8,
    #     dist=distance_plane * voxel_size)
    #
    # closest_nodes = [nodes for nodes in closest_nodes
    #                  if len(set_voxel.intersection(set(nodes))) > 0]

    # ==========================================================================

    # ==========================================================================
    # Compute width
    width = list()
    for nodes in closest_nodes:
        width.append(get_length_point_cloud(nodes))

    info['width_max'] = max(width)
    info['width_mean'] = sum(width) / float(len(width))

    # ==========================================================================
    # Compute length
    length = 0
    for n1, n2 in zip(path, path[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    info['length'] = length

    # ==========================================================================
    # Compute extremity
    info['z_tip'] = path[-1][2]
    info['z_base'] = path[0][2]

    info['position_tip'] = path[-1]
    info['position_base'] = path[0]

    # ==========================================================================
    # Compute azimuth
    if len(path) > 1:

        x, y, z = path[0]

        vectors = list()
        for i in range(1, len(path)):
            xx, yy, zz = path[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)
        info['vector_mean'] = tuple(vector_mean)

        x, y, z = vector_mean
        angle = math.atan2(y, x)
        angle = angle + 2 * math.pi if angle < 0 else angle
        info['azimuth'] = angle

    # ==========================================================================
    # # Compute angle
    # if len(path) > 2:
    #
    #     x, y, z = path[0]
    #
    #     vectors = list()
    #     for i in range(1, len(path) / 3 + 1):
    #         xx, yy, zz = path[i]
    #
    #         v = (xx - x, yy - y, zz - z)
    #         vectors.append(v)
    #
    #     vector_mean = numpy.array(vectors).mean(axis=0)
    #
    # angle_between
    # ==========================================================================

    info['voxels_size'] = voxel_size
    info['voxels_number'] = len(voxels_position)

    return info


def compute_width_organ(organ, closest_nodes):

    width = list()
    for nodes in closest_nodes:
        width.append(get_length_point_cloud(nodes))

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

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size,
        without_connexity=True)

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
                               distance_plane=0.5):

    voxels_position = mature_leaf_voxel_organ.voxels_position()
    voxels_size = mature_leaf_voxel_organ.info['voxels_size']
    polyline = mature_leaf_voxel_organ.longest_polyline()

    # ==========================================================================

    if len(polyline) <= 1:
        return mature_leaf_voxel_organ

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size)


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


def maize_cornet_leaf_analysis_real_length(organ):

    voxels_position = set(organ.voxels_position())
    polyline = organ.longest_polyline()

    if len(polyline) <= 1:
        return organ

    # ==========================================================================
    # Compute extremity

    index_position_base = len(polyline) - 1
    for i in range(len(polyline) - 1, -1, -1):
        if polyline[i] not in set(voxels_position):
            index_position_base = i
            break

    real_polyline = polyline[index_position_base:]

    length = 0
    for n1, n2 in zip(real_polyline, real_polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))
    organ.info['not_visible_length'] = length

    return organ


def maize_cornet_leaf_analysis(organ,
                               stem_vector_mean,
                               voxels,
                               distance_plane=0.5):

    voxels_position = organ.voxels_position()
    voxels_size = organ.info['voxels_size']
    polyline = organ.longest_polyline()

    if len(polyline) <= 1:
        return organ

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size)

    # ==========================================================================
    # Compute extremity
    voxels = list(set(polyline).intersection(set(voxels)))

    index_position_tip = -1
    index_position_base = 0
    for i, node in enumerate(polyline):
        if node in voxels:
            index_position_base = i

    real_polyline = polyline[index_position_base:index_position_tip]
    real_closest_nodes = closest_nodes[index_position_base:index_position_tip]

    organ = organ_analysis(organ, real_polyline, real_closest_nodes,
                           stem_vector_mean)

    return organ


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
            vo_mature_leaf,
            vo_stem.info['vector_mean'])

        lorder.append((vo_mature_leaf,
                       vo_mature_leaf.info["z_intersection"]))

    lorder.sort(key=lambda x: x[1])

    num_order = 1
    for vo, _ in lorder:
        vo.info["order"] = num_order
        num_order += 1

    lorder = list()
    for vo_cornet_leaf in voxel_maize_segmentation.get_cornet_leafs():
        vo_cornet_leaf = maize_cornet_leaf_analysis_real_length(vo_cornet_leaf)
        lorder.append((vo_cornet_leaf,
                       -vo_cornet_leaf.info["not_visible_length"]))

    voxels = set(vo_stem.voxels_position())
    lorder.sort(key=lambda x: x[1])
    for vo, _ in lorder:
        vo.info["order"] = num_order
        num_order += 1

        vo = maize_cornet_leaf_analysis(vo,
                                        vo_stem.info['vector_mean'],
                                        voxels)

        voxels = voxels.union(set(vo.voxels_position()))



    return voxel_maize_segmentation
