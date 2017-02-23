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
    compute_closest_nodes)

# ==============================================================================


def get_max_distance(node, nodes):
    max_distance = 0
    max_node = node

    for n in nodes:
        distance = abs(numpy.linalg.norm(numpy.array(node) - numpy.array(n)))
        if distance >= max_distance:
            max_distance = distance
            max_node = n

    return max_node, max_distance


def get_length_point_cloud(nodes):

    # print nodes
    # if len(nodes) >= 4:
    #     arr = numpy.array(nodes).astype(float)
    #     hull = scipy.spatial.ConvexHull(arr, qhull_options="QJ")
    #     nodes = hull.vertices

    res = scipy.spatial.distance.pdist(nodes, 'euclidean')

    if len(res) > 0:
        return res.max()
    else:
        return 0


def voxels_path_analysis(voxel, path, voxel_size,
                         higher_path, all_vs, distance_plane=0.75):

    info = dict()

    set_voxel = set(list(voxel))
    planes, closest_nodes = compute_closest_nodes(
        all_vs,
        path,
        radius=8,
        dist=distance_plane * voxel_size)

    voxels = set().union(*closest_nodes)
    voxels = list(voxels.intersection(set(higher_path)))
    z = numpy.max(numpy.array(voxels)[:, 2])

    info["z_intersection"] = z

    # ==========================================================================

    closest_nodes = [list(set_voxel.intersection(set(nodes))) for nodes in
                     closest_nodes]

    tmp_closest_nodes = list()
    tmp_path = list()

    for nodes, node in zip(closest_nodes, path):
        if len(nodes) > 0:
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

    width = list()
    for nodes in closest_nodes:
        width.append(get_length_point_cloud(nodes))

    # info['width'] = width
    info['max_width'] = max(width)
    info['mean_width'] = sum(width) / float(len(width))
    info['min_width'] = min(width)

    # ==========================================================================

    length = 0
    for n1, n2 in zip(path, path[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    # ==========================================================================

    info['length'] = length
    info['height'] = path[-1][2]
    info['base'] = path[0][2]

    # ==========================================================================

    x, y, z = path[0]
    vectors = list()
    for i in range(1, len(path)):
        xx, yy, zz = path[i]

        v = (xx - x, yy - y, zz - z)
        vectors.append(v)

    vector_mean = numpy.array(vectors).mean(axis=0)

    x, y, z = vector_mean
    angle = math.atan2(y, x)
    angle = angle + 2 * math.pi if angle < 0 else angle
    info['azimuth'] = angle

    info['vector_mean'] = tuple(vector_mean)
    info['vector_base'] = path[0]

    # ==========================================================================

    info['voxel_size'] = voxel_size
    info['number_of_voxel'] = len(voxel)

    return info


def plant_analysis(voxel_skeleton_labeled):

    plant_info = list()
    z_max = float("-inf")
    higher_path = None
    all_vs = set()
    for vsl in voxel_skeleton_labeled.voxel_segments:
        all_vs = all_vs.union(set(vsl.voxels_position))
        for polyline in vsl.polylines:
            z = numpy.max(numpy.array(polyline)[:, 2])

            if z > z_max:
                z_max = z
                higher_path = polyline

    all_vs = numpy.array(list(all_vs))

    for vsl in voxel_skeleton_labeled.voxel_segments:

        label = vsl.label
        voxels_position = vsl.voxels_position
        voxels_size = vsl.voxels_size
        polylines = vsl.polylines

        if len(polylines) > 0:
            polyline = max(polylines, key=len)
            info = voxels_path_analysis(voxels_position, polyline, voxels_size,
                                        higher_path, all_vs)
        else:
            info = dict()
            info['voxel_size'] = voxels_size
            info['number_of_voxel'] = len(voxels_position)

        info['label'] = label

        plant_info.append(info)

    return plant_info
