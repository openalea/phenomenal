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
import scipy.sparse

from openalea.phenomenal.object import VoxelGraph
# ==============================================================================

# a path of 3 nodes, and an isolated node
POSITIONS = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (5, 5, 5)]


def _graph():
    rows, cols, weights = [0, 1], [1, 2], [1.0, 1.0]
    matrix = scipy.sparse.coo_array(
        (weights + weights, (rows + cols, cols + rows)), shape=(4, 4)
    )
    return VoxelGraph(POSITIONS, 1, matrix)


def test_nodes():
    graph = _graph()
    assert graph.number_of_nodes() == len(graph) == 4
    assert graph.number_of_edges() == 2
    assert graph.nodes() == [tuple(map(float, p)) for p in POSITIONS]
    assert (1, 0, 0) in graph and (2, 2, 2) not in graph
    assert graph.index((1, 1, 0)) == 2
    assert graph.indices([(1, 1, 0), (2, 2, 2)]).tolist() == [2, -1]
    assert graph.positions([0, 3]) == {(0, 0, 0), (5, 5, 5)}


def test_neighbors_and_subgraph():
    graph = _graph()
    assert sorted(graph.neighbors((1, 0, 0))) == [(0, 0, 0), (1, 1, 0)]
    assert graph.neighbors((5, 5, 5)) == []
    sub = graph.subgraph([(1, 0, 0), (1, 1, 0), (5, 5, 5)])
    assert sub.number_of_nodes() == 3
    assert sub.number_of_edges() == 1


def test_add_edges():
    graph = _graph()
    graph.add_edges([2, 0], [3, 1], numpy.array([7.0, 2.0]))
    assert graph.number_of_edges() == 3
    assert math.isclose(graph.matrix[2, 3], 7) and math.isclose(graph.matrix[3, 2], 7)
    # an existing edge is replaced, not summed
    assert math.isclose(graph.matrix[0, 1], 2)


def test_empty_graph():
    graph = VoxelGraph(numpy.empty((0, 3)), 1)
    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0
