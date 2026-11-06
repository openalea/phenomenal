# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import numpy

from ..object import VoxelGraph
# ==============================================================================


def as_voxel_graph(graph, voxels_size):
    """Return graph as a VoxelGraph, converting a networkx graph.

    Parameters
    ----------
    graph : VoxelGraph or networkx.Graph
        Graph whose nodes are voxel center positions
    voxels_size : float
        Size of the voxels

    Returns
    -------
    graph : VoxelGraph
    """
    if isinstance(graph, VoxelGraph):
        return graph
    return VoxelGraph.from_networkx(graph, voxels_size)


def connect_all_node_with_nearest_neighbors(graph):
    """Connect all the nodes in the graph together

    Starting from the largest connected component, the closest component is
    connected by an edge between its two closest nodes, until all the nodes
    are connected.

    Parameters
    ----------
    graph : VoxelGraph

    Returns
    -------
    graph : VoxelGraph
        The same graph, modified in place.
    """
    return graph.connect_components()


def create_graph(voxels_position, voxels_size):
    """Create a graph from voxels positions and voxels_size

    Each voxel is connected to its 26 neighbors, with the distance between
    the voxel centers as weight.

    Parameters
    ----------
    voxels_position : list
        list of 3-tuple
    voxels_size : int
        Diameter size of voxels
    Returns
    -------
    graph: VoxelGraph
    """
    return VoxelGraph.from_voxels_position(voxels_position, voxels_size)


def graph_from_voxel_grid(voxel_grid, connect_all_point=True):
    """
    Return a weighted graph built from a voxel_grid object where
    each node of the graph is the tuple position of the voxels center.
    Each node is edged, if present, to the nodes depict their
    26-neighbors in the voxel_grid. The weight of each edge is the distance
    between their voxel center position.

    If connect_all_point is False, then the graph returned is the subgraph
    with the biggest connected components. If connect_all_point is True,
    the subgraph of connected components are edged via the closest neighbors
    between the subgraph with a weight equal to the distance between their
    position.

    Parameters
    ----------
    voxel_grid : VoxelGrid
    connect_all_point : bool, optional

    Returns
    -------
    graph : VoxelGraph
        Use graph.to_networkx() to get a networkx.Graph.
    """
    voxels_position = numpy.asarray(list(voxel_grid.voxels_position), dtype=float)
    graph = create_graph(voxels_position, voxel_grid.voxels_size)

    if connect_all_point:
        return connect_all_node_with_nearest_neighbors(graph)

    _, labels = graph.connected_components_labels()
    if len(labels) == 0:
        return graph
    largest = numpy.argmax(numpy.bincount(labels))
    return graph.subgraph(graph.positions(numpy.flatnonzero(labels == largest)))
