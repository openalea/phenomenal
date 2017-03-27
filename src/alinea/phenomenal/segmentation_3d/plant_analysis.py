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


def get_length_point_cloud(nodes):

    if len(nodes) == 0:
        return 0

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


def maize_stem_analysis(stem_voxel_segment, distance_plane=0.75):

    voxels_position = stem_voxel_segment.voxels_position
    voxels_size = stem_voxel_segment.voxels_size
    polyline = max(stem_voxel_segment.polylines, key=len)

    info = dict()

    # ==========================================================================
    info['voxels_size'] = voxels_size
    info['voxels_number'] = len(voxels_position)

    if len(polyline) <= 1:
        return info
    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size,
        without_connexity=True)

    # import mayavi.mlab
    # from alinea.phenomenal.display import show_voxels, plot_voxels
    #
    #
    # mayavi.mlab.figure()
    # plot_voxels(voxels_position, 2)
    # plot_voxels(polyline, 4)
    # mayavi.mlab.show()
    #
    # voxels = set().union(*closest_nodes)
    #
    # mayavi.mlab.figure()
    # plot_voxels(voxels, 2)
    # plot_voxels(polyline, 4)
    # mayavi.mlab.show()

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
    for n1, n2 in zip(polyline, polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    info['length'] = length

    # ==========================================================================
    # Compute extremity
    info['z_tip'] = polyline[-1][2]
    info['z_base'] = polyline[0][2]

    info['position_tip'] = polyline[-1]
    info['position_base'] = polyline[0]

    # ==========================================================================
    # Compute azimuth
    if len(polyline) > 1:

        x, y, z = polyline[0]

        vectors = list()
        for i in range(1, len(polyline)):
            xx, yy, zz = polyline[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)
        info['vector_mean'] = tuple(vector_mean)

    return info


def maize_mature_leaf_analysis(mature_leaf_voxel_segment,
                               stem_vector_mean,
                               distance_plane=0.5):

    voxels_position = mature_leaf_voxel_segment.voxels_position
    voxels_size = mature_leaf_voxel_segment.voxels_size
    polyline = max(mature_leaf_voxel_segment.polylines, key=len)

    info = dict()
    # ==========================================================================

    info['voxels_size'] = voxels_size
    info['voxels_number'] = len(voxels_position)

    if len(polyline) <= 1:
        return info

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size)

    # ==========================================================================
    tmp_closest_nodes = list()
    tmp_polyline = list()

    for nodes, node in zip(closest_nodes, polyline):
        if len(nodes) > 0 and node in set(nodes):
            tmp_closest_nodes.append(nodes)
            tmp_polyline.append(node)

    polyline = tmp_polyline
    closest_nodes = tmp_closest_nodes

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
    for n1, n2 in zip(polyline, polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    info['length'] = length

    # ==========================================================================
    # Compute extremity
    info['z_tip'] = polyline[-1][2]
    info['z_base'] = polyline[0][2]

    info["z_intersection"] = polyline[0][2]
    info["position_intersection"] = polyline[0]

    info['position_tip'] = polyline[-1]
    info['position_base'] = polyline[0]

    # ==========================================================================
    # Compute azimuth

    x, y, z = polyline[0]

    vectors = list()
    for i in range(1, len(polyline)):
        xx, yy, zz = polyline[i]

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

    if len(polyline) > 3:

        x, y, z = polyline[0]

        vectors = list()
        for i in range(1, len(polyline) / 4 + 1):
            xx, yy, zz = polyline[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)

        info['vector_mean_one_quarter'] = tuple(vector_mean)
        info['angle'] = angle_between(vector_mean, stem_vector_mean)

    return info


def maize_cornet_leaf_analysis(cornet_leaf_voxel_segment,
                               stem_vector_mean,
                               voxels_higher_path,
                               all_vs,
                               distance_plane=0.5):

    voxels_position = cornet_leaf_voxel_segment.voxels_position
    voxels_size = cornet_leaf_voxel_segment.voxels_size
    polyline = max(cornet_leaf_voxel_segment.polylines, key=len)

    info = dict()
    # ==========================================================================

    info['voxels_size'] = voxels_size
    info['voxels_number'] = len(voxels_position)

    if len(polyline) <= 1:
        return info

    # ==========================================================================
    # Compute height of the leaf

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(voxels_position)),
        polyline,
        radius=8,
        dist=distance_plane * voxels_size)

    voxels = list(set(voxels_position).intersection(set(voxels_higher_path)))
    z = numpy.max(numpy.array(voxels)[:, 2])
    index = numpy.argmax(numpy.array(voxels)[:, 2])

    info["z_intersection"] = z
    info["position_intersection"] = tuple(numpy.array(voxels)[index])

    # ==========================================================================
    tmp_closest_nodes = list()
    tmp_polyline = list()

    index = 0
    for nodes, node in zip(closest_nodes, polyline):
        if len(nodes) > 0 and node in set(nodes):
            tmp_closest_nodes.append(nodes)
            tmp_polyline.append(node)

            if info["position_intersection"] in set(nodes):
                index = len(tmp_polyline)

    polyline = tmp_polyline
    visible_polyline = tmp_polyline[index:]
    closest_nodes = tmp_closest_nodes

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
    for n1, n2 in zip(polyline, polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))
    info['length'] = length

    # ==========================================================================
    # Compute length
    length = 0
    for n1, n2 in zip(visible_polyline, visible_polyline[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))
    info['visible_length'] = length

    # ==========================================================================
    # Compute extremity
    info['z_tip'] = polyline[-1][2]
    info['z_base'] = polyline[0][2]

    info['position_tip'] = polyline[-1]
    info['position_base'] = polyline[0]

    # ==========================================================================
    # Compute azimuth

    x, y, z = polyline[0]

    vectors = list()
    for i in range(1, len(polyline)):
        xx, yy, zz = polyline[i]

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

    if len(polyline) > 3:

        x, y, z = polyline[0]

        vectors = list()
        for i in range(1, len(polyline) / 4 + 1):
            xx, yy, zz = polyline[i]

            v = (xx - x, yy - y, zz - z)
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)

        info['vector_mean_one_quarter'] = tuple(vector_mean)
        info['angle'] = angle_between(vector_mean, stem_vector_mean)

    return info


def maize_analysis(voxel_skeleton_labeled, distance_plane=0.5):


    # from alinea.phenomenal.display import show_voxel_skeleton
    #
    # show_voxel_skeleton(voxel_skeleton_labeled, with_voxels=True)
    #
    # import mayavi.mlab
    # from alinea.phenomenal.display import show_voxels, plot_voxels
    #
    # for vsl in voxel_skeleton_labeled.voxel_segments:
    #
    #     mayavi.mlab.figure()
    #     for polyline in vsl.polylines:
    #         plot_voxels(polyline, 2)
    #
    #     plot_voxels(vsl.voxels_position, 2)
    #
    #     mayavi.mlab.show()
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

    voxels_size = voxel_skeleton_labeled.get_voxels_size()

    closest_nodes = compute_closest_nodes_with_planes(
        numpy.array(list(all_vs)),
        higher_path,
        radius=8,
        dist=distance_plane * voxels_size)
    voxels_higher_path = set().union(*closest_nodes)

    vs_stem = voxel_skeleton_labeled.get_stem()
    vs_stem.info = maize_stem_analysis(vs_stem)

    for vs_mature_leaf in voxel_skeleton_labeled.get_mature_leafs():
        vs_mature_leaf.info = maize_mature_leaf_analysis(
            vs_mature_leaf, vs_stem.info['vector_mean'])

    for vs_cornet_leaf in voxel_skeleton_labeled.get_cornet_leafs():

        vs_cornet_leaf.info = maize_cornet_leaf_analysis(
            vs_cornet_leaf, vs_stem.info['vector_mean'], voxels_higher_path, all_vs)

    vs_unknown = voxel_skeleton_labeled.get_unknown()
    vs_unknown.info = dict()
    vs_unknown.info['voxels_size'] = vs_unknown.voxels_size
    vs_unknown.info['voxels_number'] = len(vs_unknown.voxels_position)

    for vs in voxel_skeleton_labeled.voxel_segments:
        vs.info['label'] = vs.label

    return voxel_skeleton_labeled
