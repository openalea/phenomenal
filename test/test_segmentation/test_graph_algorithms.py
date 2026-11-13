# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
import math

import numpy

from openalea.phenomenal.segmentation.graph import (
    connect_all_node_with_nearest_neighbors,
    connected_components,
    create_graph,
    number_connected_components,
    path,
    shortest_paths_tree,
    walk,
)
# ==============================================================================

# two groups of voxels, 3 voxels apart
POSITIONS = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1), (6, 2, 1), (6, 3, 1)]


def test_create_graph_neighbors_and_weights():
    graph = create_graph(POSITIONS, 1)
    assert graph.number_of_nodes() == 6
    assert graph.number_of_edges() == 5
    assert sorted(graph.neighbors((1, 1, 0))) == [(0, 0, 0), (1, 0, 0), (2, 2, 1)]
    i, j = graph.index((1, 1, 0)), graph.index((2, 2, 1))
    assert math.isclose(graph.matrix[i, j], math.sqrt(3))


def test_create_graph_empty():
    assert create_graph([], 1).number_of_nodes() == 0


def test_components_and_connection():
    graph = create_graph(POSITIONS, 1)
    components = sorted(connected_components(graph), key=len)
    assert components == [{(6, 2, 1), (6, 3, 1)}, {(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1)}]
    sub = graph.subgraph([(0, 0, 0), (1, 0, 0), (6, 2, 1)])
    assert number_connected_components(sub) == 2
    assert connect_all_node_with_nearest_neighbors(graph) is graph
    assert number_connected_components(graph) == 1
    i, j = graph.index((2, 2, 1)), graph.index((6, 2, 1))
    assert math.isclose(graph.matrix[i, j], 4)


def test_shortest_paths():
    graph = connect_all_node_with_nearest_neighbors(create_graph(POSITIONS, 1))
    source = graph.index((0, 0, 0))
    predecessors, lengths = shortest_paths_tree(graph, source)
    end = graph.index((6, 3, 1))
    nodes = [graph.nodes()[i] for i in path(predecessors, end)]
    assert nodes == [(0, 0, 0), (1, 1, 0), (2, 2, 1), (6, 2, 1), (6, 3, 1)]
    assert lengths[end] == 5
    assert lengths[source] == 1


def test_walk():
    graph = connect_all_node_with_nearest_neighbors(create_graph(POSITIONS, 1))
    source = graph.index((0, 0, 0))
    left = {(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1)}
    # walk through the nodes with x < 3
    walked = walk(graph, source, lambda p: p[:, 0] < 3)
    assert graph.positions(walked) == left
    allowed = numpy.ones(graph.number_of_nodes(), dtype=bool)
    allowed[graph.index((1, 1, 0))] = False
    walked = walk(graph, source, lambda p: p[:, 0] < 3, allowed)
    assert graph.positions(walked) == {(0, 0, 0), (1, 0, 0)}


def test_walk_reuses_seen():
    graph = connect_all_node_with_nearest_neighbors(create_graph(POSITIONS, 1))
    seen = numpy.zeros(graph.number_of_nodes(), dtype=bool)
    for _ in range(2):
        walked = walk(graph, graph.index((0, 0, 0)), lambda p: p[:, 0] < 3, seen=seen)
        assert len(walked) == 4
        assert not seen.any()
