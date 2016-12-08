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
import networkx
import scipy.spatial

from alinea.phenomenal.segmentation_3d.algorithm import (
    merge)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

from alinea.phenomenal.segmentation_3d.graph import (
    create_graph)

from alinea.phenomenal.data_structure import voxel_centers_to_image_3d

from alinea.phenomenal.display.segmentation3d import show_list_points_3d
# ==============================================================================


def find_base_stem_position(voxel_centers, voxel_size, neighbor_size=50):

    image_3d = voxel_centers_to_image_3d(voxel_centers, voxel_size)

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxel_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxel_size))

    k = neighbor_size / voxel_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[max(x - k, 0): min(x + k, x_len),
                   max(y - k, 0): min(y + k, y_len),
                   :]

    xx, yy, zz = numpy.where(roi == 1)

    min_z_value = numpy.min(zz)
    index_min_z_value = numpy.where(zz == min_z_value)
    mean_float_point = numpy.array([numpy.mean(xx[index_min_z_value]),
                                    numpy.mean(yy[index_min_z_value]),
                                    numpy.mean(zz[index_min_z_value])])

    mean_point = None
    min_dist = float('inf')
    for xxx, yyy, zzz in zip(xx, yy, zz):
        pt = numpy.array([xxx, yyy, zzz])
        dist = numpy.linalg.norm(mean_float_point - pt)
        if dist < min_dist:
            min_dist = dist
            mean_point = pt

    stem_base_position = (max(x - k, 0) + mean_point[0],
                          max(y - k, 0) + mean_point[1],
                          mean_point[2])

    pos = numpy.array(stem_base_position)
    pos = pos * voxel_size + image_3d.world_coordinate

    return pos


def fusion_graph(graph):

    connected_component = list(networkx.connected_component_subgraphs(
        graph, copy=False))

    nodes_connected_component = [cc.nodes() for cc in connected_component]

    while len(nodes_connected_component) > 1:

        nodes_src = nodes_connected_component[0]
        nodes_dst = set()
        nodes_connected_component = nodes_connected_component[1:]

        pt1 = None
        pt2 = None
        min_dist = float('inf')

        for nodes in nodes_connected_component:

            result = scipy.spatial.distance.cdist(nodes_src, nodes, 'euclidean')

            min1 = result.min(axis=1)
            m = min1.min(axis=0)

            if m < min_dist:
                min_dist = m

                dst_index = numpy.argmin(result, axis=1)
                src_index = numpy.argmin(min1, axis=0)

                pt1 = nodes_src[src_index]
                pt2 = nodes[dst_index[src_index]]

                nodes_dst = nodes

        nodes_connected_component.remove(nodes_dst)
        nodes_connected_component.append(list(set(nodes_src).union(nodes_dst)))
        graph.add_edge(pt1, pt2, weight=min_dist)

    return graph


def graph_skeletonize(voxel_centers, voxel_size):
    # ==========================================================================
    # Graph creation
    graph = create_graph(voxel_centers, voxel_size=voxel_size)

    graph = fusion_graph(graph)
    # # Keep the biggest connected components
    # graph = max(networkx.connected_component_subgraphs(graph, copy=False),
    #             key=len)

    # Keep the voxel cloud of the biggest component
    biggest_component_voxel_centers = graph.nodes()

    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    x_stem, y_stem, z_stem = find_base_stem_position(
        graph.nodes(), voxel_size)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return graph, biggest_component_voxel_centers, all_shorted_path_to_stem_base


def segment_path(voxels, array_voxels,
                 skeleton_path,
                 graph,
                 distance_plane=0.75):

    # ==========================================================================
    # Get the longest shorted path of voxels

    leaf_skeleton_path = None
    longest_length = 0
    for node in voxels:
        p = skeleton_path[node]

        if len(p) > longest_length:
            longest_length = len(p)
            leaf_skeleton_path = p

    # ==========================================================================

    if leaf_skeleton_path:

        planes, closest_nodes = compute_closest_nodes(
            array_voxels,
            leaf_skeleton_path,
            radius=8,
            dist=distance_plane,
            graph=graph)

        leaf = set().union(*closest_nodes)
        remain = set(voxels).difference(leaf)

        leaf, leaf_neighbors, connected_components_remain = merge(
            graph, leaf, remain)

        remain = set().union(*connected_components_remain)

        return leaf, remain, leaf_skeleton_path


def skeletonize(voxels_plant, voxel_size, distance_plane=1.0):

    # ==========================================================================
    # Build skeleton of plant with graph of shorted path

    graph, biggest_connected_voxels_plant, skeleton_path = \
        graph_skeletonize(voxels_plant, voxel_size)

    # voxel_plant_not_connected = set(graph.nodes()).difference(set(voxels_plant))

    # ==========================================================================
    voxels_plant = biggest_connected_voxels_plant
    arr_voxels_plant = numpy.array(biggest_connected_voxels_plant)
    # ==========================================================================

    remain = voxels_plant
    segment = list()

    while len(remain) != 0:

        segment_voxel, remain, segment_ske_path = segment_path(
            remain, arr_voxels_plant, skeleton_path, graph,
            distance_plane=distance_plane * voxel_size)

        segment.append((segment_voxel, segment_ske_path))

        # show_list_points_3d([remain, segment_voxel, segment_ske_path])

    return segment, graph

