# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""Graphs of voxel centers (VoxelGraph): construction and graph algorithms."""

import itertools

import numpy
import scipy.sparse
import scipy.sparse.csgraph
import scipy.spatial

from ..object import VoxelGraph

__all__ = [
    "connect_all_node_with_nearest_neighbors",
    "create_graph",
    "graph_from_voxel_grid",
    "connected_components_labels",
    "connected_components",
    "number_connected_components",
    "shortest_paths_tree",
    "path",
    "walk",
]
# ==============================================================================


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
    n, labels = connected_components_labels(graph)
    if n <= 1:
        return graph
    positions = graph.voxels_position
    groups = [numpy.flatnonzero(labels == k) for k in range(n)]
    src = max(range(n), key=lambda k: len(groups[k]))
    remaining = [k for k in range(n) if k != src]
    # closest distance of each remaining component to the connected nodes,
    # with its node and the connected node
    best = {k: (numpy.inf, -1, -1) for k in remaining}

    def update(new_group):
        tree = scipy.spatial.cKDTree(positions[new_group])
        for k in remaining:
            distance, index = tree.query(positions[groups[k]])
            i = int(numpy.argmin(distance))
            if distance[i] < best[k][0]:
                best[k] = (float(distance[i]), groups[k][i], new_group[index[i]])

    update(groups[src])
    edges = []
    while remaining:
        k = min(remaining, key=lambda c: best[c][0])
        distance, i, j = best.pop(k)
        remaining.remove(k)
        edges.append((i, j, distance))
        if remaining:
            update(groups[k])
    index_1, index_2, weights = zip(*edges)
    graph.add_edges(index_1, index_2, numpy.array(weights))
    return graph


def create_graph(voxels_position, voxels_size):
    """Create a graph from voxels positions and voxels_size

    Each voxel is connected to its 26 neighbors, with the distance between
    the voxel centers as weight. A voxel is a neighbor if its position is
    exactly the voxel position plus a combination of -voxels_size, 0,
    voxels_size on each axis.

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
    positions = numpy.asarray(voxels_position, dtype=float).reshape(-1, 3)
    n = len(positions)
    if n == 0:
        return VoxelGraph(positions, voxels_size)

    offsets = numpy.array(
        [o for o in itertools.product((-1, 0, 1), repeat=3) if o != (0, 0, 0)]
    )
    neighbors = offsets * voxels_size
    distances = numpy.linalg.norm(neighbors, axis=1)

    # Find the neighbors with integer cell indices of the voxels in the
    # grid, then keep the pairs where position + offset is exactly the
    # neighbor position.
    cells = numpy.rint((positions - positions.min(axis=0)) / voxels_size)
    cells = cells.astype(numpy.int64) + 1
    dims = cells.max(axis=0) + 2
    keys = numpy.ravel_multi_index(cells.T, dims)
    order = numpy.argsort(keys, kind="stable")
    sorted_keys = keys[order]
    neighbors_keys = numpy.ravel_multi_index(
        (cells[:, None, :] + offsets).transpose(2, 0, 1), dims
    )
    found = numpy.searchsorted(sorted_keys, neighbors_keys).clip(max=n - 1)
    index_voxel, index_offset = numpy.nonzero(sorted_keys[found] == neighbors_keys)
    index_neighbor = order[found[index_voxel, index_offset]]
    exact = numpy.all(
        positions[index_voxel] + neighbors[index_offset] == positions[index_neighbor],
        axis=1,
    )
    matrix = scipy.sparse.coo_array(
        (
            distances[index_offset[exact]],
            (index_voxel[exact], index_neighbor[exact]),
        ),
        shape=(n, n),
    )
    return VoxelGraph(positions, voxels_size, matrix)


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
    """
    voxels_position = numpy.asarray(list(voxel_grid.voxels_position), dtype=float)
    graph = create_graph(voxels_position, voxel_grid.voxels_size)

    if connect_all_point:
        return connect_all_node_with_nearest_neighbors(graph)

    _, labels = connected_components_labels(graph)
    if len(labels) == 0:
        return graph
    largest = numpy.argmax(numpy.bincount(labels))
    return graph.subgraph(graph.positions(numpy.flatnonzero(labels == largest)))


# ==============================================================================
# Connected components


def connected_components_labels(graph):
    """Number of connected components, and component label of each node.

    Parameters
    ----------
    graph : VoxelGraph

    Returns
    -------
    n : int
    labels : numpy.ndarray
        Component label (0..n-1) of each node index.
    """
    return scipy.sparse.csgraph.connected_components(graph.matrix, directed=False)


def connected_components(graph):
    """List of the connected components of graph, as sets of node positions."""
    n, labels = connected_components_labels(graph)
    order = numpy.argsort(labels, kind="stable")
    bounds = numpy.cumsum(numpy.bincount(labels, minlength=n))[:-1]
    return [graph.positions(group) for group in numpy.split(order, bounds)]


def number_connected_components(graph):
    """Number of connected components of graph."""
    return connected_components_labels(graph)[0]


# ==============================================================================
# Shortest paths


def shortest_paths_tree(graph, source):
    """Shortest paths (Dijkstra) from the node index source.

    Parameters
    ----------
    graph : VoxelGraph
    source : int
        Index of the start node.

    Returns
    -------
    predecessors : numpy.ndarray
        Previous node index on the shortest path, -9999 for source
        and the unreachable nodes.
    lengths : numpy.ndarray
        Number of nodes of the shortest path from source (1 for source,
        0 for the unreachable nodes).
    """
    distances, predecessors = scipy.sparse.csgraph.dijkstra(
        graph.matrix, directed=False, indices=source, return_predecessors=True
    )
    lengths = numpy.zeros(len(distances), dtype=numpy.int64)
    lengths[source] = 1
    reachable = numpy.flatnonzero(numpy.isfinite(distances))
    # a predecessor is always closer to source than its successor
    for i in reachable[numpy.argsort(distances[reachable], kind="stable")].tolist():
        if i != source:
            lengths[i] = lengths[predecessors[i]] + 1
    return predecessors, lengths


def path(predecessors, target):
    """Node indices of the path ending at target, from the source.

    Parameters
    ----------
    predecessors : numpy.ndarray
        As returned by shortest_paths_tree.
    target : int
        Index of the last node.
    """
    nodes = [target]
    while predecessors[nodes[-1]] >= 0:
        nodes.append(int(predecessors[nodes[-1]]))
    return nodes[::-1]


# ==============================================================================
# Walk


def walk(graph, source, accept, allowed=None, seen=None):
    """Nodes connected to source through accepted nodes (breadth-first).

    Parameters
    ----------
    graph : VoxelGraph
    source : int
        Index of the start node. It must be accepted.
    accept : callable
        accept(positions) returns a boolean array: True for the positions
        (array (k, 3)) of the nodes that the walk can go through.
    allowed : numpy.ndarray, optional
        Boolean array over the nodes: the walk only goes through allowed
        nodes.
    seen : numpy.ndarray, optional
        Boolean array over the nodes, all False, used as working memory and
        reset to all False on return. Pass the same array to repeated walks
        on a big graph, to avoid allocating it at each walk.

    Returns
    -------
    indices : numpy.ndarray
        Indices of the connected nodes, source included.
    """
    if seen is None:
        seen = numpy.zeros(graph.number_of_nodes(), dtype=bool)
    indptr, indices = graph.matrix.indptr, graph.matrix.indices
    frontier = numpy.array([source])
    seen[source] = True
    touched, connected = [frontier], [frontier]
    while len(frontier):
        starts, stops = indptr[frontier], indptr[frontier + 1]
        counts = stops - starts
        starts, stops, counts = starts[counts > 0], stops[counts > 0], counts[counts > 0]
        total = counts.sum()
        if total == 0:
            break
        # indices[starts[k]:stops[k]] for all k, without a python loop
        steps = numpy.ones(total, dtype=numpy.int64)
        first = numpy.cumsum(counts)[:-1]
        steps[0] = starts[0]
        steps[first] = starts[1:] - stops[:-1] + 1
        candidates = indices[numpy.cumsum(steps)]
        candidates = numpy.unique(candidates[~seen[candidates]])
        if allowed is not None:
            candidates = candidates[allowed[candidates]]
        seen[candidates] = True
        touched.append(candidates)
        frontier = candidates[accept(graph.voxels_position[candidates])]
        connected.append(frontier)
    seen[numpy.concatenate(touched)] = False
    return numpy.concatenate(connected)
