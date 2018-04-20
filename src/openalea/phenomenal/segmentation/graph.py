# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
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

from ..object import VoxelGrid
# ==============================================================================


def connect_all_node_with_nearest_neighbors(graph):
    """ Connect all the nodes in the graph together

    Parameters
    ----------
    graph : networkx.Graph

    Returns
    -------
    graph : networkx.Graph
    """
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


def create_graph(voxels_position, voxels_size):
    """ Create a networkx.graph from voxels positions and voxels_size

    Parameters
    ----------
    voxels_position : list
        list of 3-tuple
    voxels_size : int
        Diameter size of voxels
    Returns
    -------
    graph: networkx.Graph
    """

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


def _create_graph_with_sklearn(voxels_position, voxels_size):
    """
    Implementation not used to create a graph with scikit-learn function

    Parameters
    ----------
    voxels_position
    voxels_size

    Returns
    -------
    graph : networkx.Graph

    """
    vpc = VoxelGrid(voxels_position, voxels_size)

    image = vpc.to_image_3d()

    sparse_matrix = sklearn.feature_extraction.image.img_to_graph(image)

    graph = networkx.from_scipy_sparse_matrix(sparse_matrix)

    indices = numpy.where(image.ravel() >= 1)

    indices = list(indices[0])
    graph = graph.subgraph(indices)

    return graph


def graph_from_voxel_grid(voxel_grid, connect_all_point=True):
    """
    Return a weigthed networkx graph builded from a voxel_grid object where
    each node of the graph is the tuple position of the voxels center.
    Each node are edged, if present, to the nodes depict their
    26-neigbors in the voxel_grid. The weigth of each edge is the distance
    between their voxel center position.

    If connect_all_point is False, then the graph returned is the subgraph
    with the biggest connected components. If connect_all_point is True,
    the subgraph of connected components are edged via the closest neighbors
    between the subgraph with a weigth equal to the distance between their
    position.

    Parameters
    ----------
    voxel_grid : VoxelGrid
    connect_all_point : bool, optional

    Returns
    -------
    graph : networkx.Graph
    """
    voxels_size = int(voxel_grid.voxels_size)
    voxels_position = map(tuple, list(voxel_grid.voxels_position))

    # ==========================================================================
    # Graph creation
    graph = create_graph(voxels_position, voxels_size)

    if connect_all_point:
        graph = connect_all_node_with_nearest_neighbors(graph)
    else:
        # Keep the biggest connected components
        graph = max(networkx.connected_component_subgraphs(graph, copy=False),
                    key=len)

    return graph


