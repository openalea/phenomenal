# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


try:
    import nx_cugraph as networkx
except ImportError:
    import networkx
import numpy
import sklearn.feature_extraction.image
import sklearn.neighbors

from ..object import VoxelGrid
# ==============================================================================


def connect_all_node_with_nearest_neighbors(graph):
    """Connect all the nodes in the graph together

    Parameters
    ----------
    graph : networkx.Graph

    Returns
    -------
    graph : networkx.Graph
    """
    # connected_component = list(networkx.connected_component_subgraphs(
    #     graph, copy=False))

    connected_component = [
        graph.subgraph(c) for c in networkx.connected_components(graph)
    ]

    nodes_connected_component = [list(cc.nodes()) for cc in connected_component]

    nodes_src = max(nodes_connected_component, key=len)
    nodes_connected_component.remove(nodes_src)

    while len(nodes_connected_component) > 0:
        neigh = sklearn.neighbors.NearestNeighbors(n_neighbors=1)
        neigh.fit(nodes_src)

        min_dist = float("inf")
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
    """Create a networkx.graph from voxels positions and voxels_size

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
    neighbors = numpy.array(
        [
            (-vs, -vs, -vs),
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
            (vs, vs, vs),
        ]
    )

    distances = numpy.linalg.norm(neighbors, axis=1)
    if len(voxels_position) == 0:
        return graph

    # Find the neighbors with integer cell indices of the voxels in the grid,
    # then keep the pairs where position + neighbor offset is exactly the
    # neighbor position, as with graph.has_node(position + offset)
    arr_vs = numpy.array(voxels_position, dtype=float)
    cells = numpy.rint((arr_vs - arr_vs.min(axis=0)) / vs).astype(numpy.int64) + 1
    offsets = numpy.rint(neighbors / vs).astype(numpy.int64)
    dims = cells.max(axis=0) + 2
    keys = numpy.ravel_multi_index(cells.T, dims)
    order = numpy.argsort(keys, kind="stable")
    sorted_keys = keys[order]
    neighbors_keys = numpy.ravel_multi_index(
        (cells[:, None, :] + offsets).transpose(2, 0, 1), dims
    )
    found = numpy.searchsorted(sorted_keys, neighbors_keys).clip(max=len(keys) - 1)
    is_neighbor = sorted_keys[found] == neighbors_keys
    # sorted by voxel, then by neighbor: the order of the edges in the loop
    # graph.add_edge(position, position + offset) over voxels and offsets
    index_voxel, index_offset = numpy.nonzero(is_neighbor)
    index_neighbor = order[found[index_voxel, index_offset]]
    exact = numpy.all(
        arr_vs[index_voxel] + neighbors[index_offset] == arr_vs[index_neighbor],
        axis=1,
    )
    index_voxel = index_voxel[exact].tolist()
    index_offset = index_offset[exact]
    index_neighbor = index_neighbor[exact].tolist()
    graph.add_weighted_edges_from(
        zip(
            (voxels_position[i] for i in index_voxel),
            (voxels_position[i] for i in index_neighbor),
            distances[index_offset],
        )
    )

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

    image = vpc.image_3d

    sparse_matrix = sklearn.feature_extraction.image.img_to_graph(image)

    graph = networkx.from_scipy_sparse_matrix(sparse_matrix)

    indices = numpy.where(image.ravel() >= 1)

    indices = list(indices[0])
    graph = graph.subgraph(indices)

    return graph


def graph_from_voxel_grid(voxel_grid, connect_all_point=True):
    """
    Return a weighted networkx graph built from a voxel_grid object where
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
    graph : networkx.Graph
    """
    voxels_size = voxel_grid.voxels_size
    voxels_position = list(map(tuple, list(voxel_grid.voxels_position)))

    # ==========================================================================
    # Graph creation
    graph = create_graph(voxels_position, voxels_size)

    if connect_all_point:
        graph = connect_all_node_with_nearest_neighbors(graph)
    else:
        graph = max(
            [graph.subgraph(c) for c in networkx.connected_components(graph)],
            key=lambda g: g.number_of_nodes(),
        )

    return graph
