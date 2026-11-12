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

from openalea.phenomenal.object import VoxelGraph
# ==============================================================================

# two groups of voxels, 3 voxels apart
POSITIONS = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1), (6, 2, 1), (6, 3, 1)]


def test_neighbors_and_weights():
    graph = VoxelGraph.from_voxels_position(POSITIONS, 1)
    assert graph.number_of_nodes() == 6
    assert graph.number_of_edges() == 5
    assert sorted(graph.neighbors((1, 1, 0))) == [(0, 0, 0), (1, 0, 0), (2, 2, 1)]
    i, j = graph.index((1, 1, 0)), graph.index((2, 2, 1))
    assert math.isclose(graph.matrix[i, j], math.sqrt(3))
    assert (0, 0, 0) in graph and (5, 5, 5) not in graph


def test_components_and_connection():
    graph = VoxelGraph.from_voxels_position(POSITIONS, 1)
    components = sorted(graph.connected_components(), key=len)
    assert components == [{(6, 2, 1), (6, 3, 1)}, {(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1)}]
    sub = graph.subgraph([(0, 0, 0), (1, 0, 0), (6, 2, 1)])
    assert sub.number_connected_components() == 2
    graph.connect_components()
    assert graph.number_connected_components() == 1
    i, j = graph.index((2, 2, 1)), graph.index((6, 2, 1))
    assert math.isclose(graph.matrix[i, j], 4)


def test_shortest_paths_and_walk():
    graph = VoxelGraph.from_voxels_position(POSITIONS, 1).connect_components()
    source = graph.index((0, 0, 0))
    predecessors, lengths = graph.shortest_paths_tree(source)
    end = graph.index((6, 3, 1))
    path = [graph.nodes()[i] for i in graph.path(predecessors, end)]
    assert path == [(0, 0, 0), (1, 1, 0), (2, 2, 1), (6, 2, 1), (6, 3, 1)]
    assert lengths[end] == 5
    # walk through the nodes with x < 3
    walked = graph.walk(source, lambda p: p[:, 0] < 3)
    assert graph.positions(walked) == {(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 2, 1)}
    allowed = numpy.ones(graph.number_of_nodes(), dtype=bool)
    allowed[graph.index((1, 1, 0))] = False
    walked = graph.walk(source, lambda p: p[:, 0] < 3, allowed)
    assert graph.positions(walked) == {(0, 0, 0), (1, 0, 0)}
