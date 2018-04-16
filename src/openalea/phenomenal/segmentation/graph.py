# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import networkx
import numpy
import sklearn.feature_extraction.image
import sklearn.neighbors

from ..object import (VoxelGraph, VoxelGrid)
# ==============================================================================


def voxel_graph_from_voxel_grid(voxel_grid,
                                connect_all_point=True):

    voxels_size = int(voxel_grid.voxels_size)
    voxels_position = map(tuple, list(voxel_grid.voxels_position))

    # ==========================================================================
    # Graph creation
    graph = create_graph(voxels_position, voxels_size=voxels_size)

    if connect_all_point:
        graph = connect_all_node_with_nearest_neighbors(graph)
    else:
        # Keep the biggest connected components
        graph = max(networkx.connected_component_subgraphs(graph, copy=False),
                    key=len)

    return VoxelGraph(graph, voxels_size)


def connect_all_node_with_nearest_neighbors(graph):

    connected_component = list(networkx.connected_component_subgraphs(
        graph, copy=False))

    nodes_connected_component = [list(cc.nodes()) for cc in connected_component]

    nodes_src = max(nodes_connected_component, key=len)
    nodes_connected_component.remove(nodes_src)

    while len(nodes_connected_component) > 0:

        neigh = sklearn.neighbors.NearestNeighbors(n_neighbors=1)
        neigh.fit(nodes_src)

        min_dist = float('inf')
        pt_1, pt_2, nodes_dst = None, None, None

        for nodes in nodes_connected_component:
            distance, index_nodes = neigh.kneighbors(nodes)

            index_min = int(numpy.argmin(distance))
            dist = distance[index_min][0]
            if dist < min_dist:
                min_dist = dist
                pt_1 = nodes[index_min]
                pt_2 = nodes_src[index_nodes[index_min][0]]
                nodes_dst = nodes

        nodes_connected_component.remove(nodes_dst)
        nodes_src = list(set(nodes_src).union(nodes_dst))
        graph.add_edge(pt_1, pt_2, weight=min_dist)

    return graph


def create_graph(voxels_position, voxels_size=1):

    graph = networkx.Graph()
    graph.add_nodes_from(voxels_position)

    vs = voxels_size
    neighbors = numpy.array([(-vs, -vs, -vs),
                             (-vs, -vs, 0),
                             (-vs, -vs, vs),

                             (-vs, 0, -vs),
                             (-vs, 0, 0),
                             (-vs, 0, vs),

                             (-vs, vs, -vs),
                             (-vs, vs, 0),
                             (-vs, vs, vs),

                             (0, -vs, -vs),
                             (0, -vs, 0),
                             (0, -vs, vs),

                             (0, 0, -vs),
                             (0, 0, vs),

                             (0, vs, -vs),
                             (0, vs, 0),
                             (0, vs, vs),

                             (vs, -vs, -vs),
                             (vs, -vs, 0),
                             (vs, -vs, vs),

                             (vs, 0, -vs),
                             (vs, 0, 0),
                             (vs, 0, vs),

                             (vs, vs, -vs),
                             (vs, vs, 0),
                             (vs, vs, vs)])

    arr_vs = numpy.array(voxels_position)
    distances = numpy.linalg.norm(neighbors, axis=1)

    for i, pt in enumerate(voxels_position):
        neighbors_position = map(tuple, neighbors + arr_vs[i])
        for j, pos in enumerate(neighbors_position):
            if graph.has_node(pos):
                graph.add_edge(pt, pos, weight=distances[j])

    return graph


def create_graph_with_sklearn(voxels_position, voxels_size):

    vpc = VoxelGrid(voxels_position, voxels_size)

    image = vpc.to_image_3d()

    sparse_matrix = sklearn.feature_extraction.image.img_to_graph(image)

    graph = networkx.from_scipy_sparse_matrix(sparse_matrix)

    indices = numpy.where(image.ravel() >= 1)

    indices = list(indices[0])
    graph = graph.subgraph(indices)

    return graph


def add_nodes(graph, voxels_position, voxels_size=1):

    graph.add_nodes_from(voxels_position)

    vs = voxels_size
    ijk = [(-vs, -vs, -vs), (-vs, -vs, 0), (-vs, -vs, vs),
           (-vs, 0, -vs), (-vs, 0, 0), (-vs, 0, vs),
           (-vs, vs, -vs), (-vs, vs, 0), (-vs, vs, vs),
           (0, -vs, -vs), (0, -vs, 0), (0, -vs, vs),
           (0, 0, -vs), (0, 0, 0), (0, 0, vs),
           (0, vs, -vs), (0, vs, 0), (0, vs, vs),
           (vs, -vs, -vs), (vs, -vs, 0), (vs, -vs, vs),
           (vs, 0, -vs), (vs, 0, 0), (vs, 0, vs),
           (vs, vs, -vs), (vs, vs, 0), (vs, vs, vs)]

    for pt in voxels_position:
        for i, j, k in ijk:
            pos = pt[0] + i, pt[1] + j, pt[2] + k
            if graph.has_node(pos):
                d = numpy.linalg.norm(numpy.array(pt) - numpy.array(pos))
                graph.add_edge(pt, pos, weight=d)

    return graph
