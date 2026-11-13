# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""Graph of voxel centers, stored as a scipy sparse matrix."""

import numpy
import scipy.sparse

# ==============================================================================


class VoxelGraph:
    """Weighted undirected graph of voxel centers.

    Each node is a voxel center position (a 3-tuple). Nodes are also numbered
    0..N-1, in the order of voxels_position. Edges are stored in matrix, a
    symmetric scipy sparse matrix of the edge weights (distances).

    This class only stores the graph and gives access to its nodes and edges.
    The graph algorithms (construction from voxel positions, connected
    components, shortest paths, walk) are the functions of
    openalea.phenomenal.segmentation.graph.

    Parameters
    ----------
    voxels_position : array-like
        (N, 3) positions of the voxel centers, one per node.
    voxels_size : float
        Size of the voxels.
    matrix : scipy sparse matrix, optional
        (N, N) symmetric matrix of the edge weights. No edges if None.
    """

    def __init__(self, voxels_position, voxels_size, matrix=None):
        self.voxels_position = numpy.asarray(voxels_position, dtype=float).reshape(-1, 3)
        self.voxels_size = voxels_size
        n = len(self.voxels_position)
        if matrix is None:
            matrix = scipy.sparse.csr_array((n, n), dtype=float)
        self.matrix = scipy.sparse.csr_array(matrix, dtype=float)
        self.matrix.sort_indices()
        self._nodes = None
        self._index = None

    # ==========================================================================
    # Edges

    def add_edges(self, index_1, index_2, weights):
        """Add (or replace) the edges between nodes index_1[k] and index_2[k]."""
        n = self.number_of_nodes()
        index_1, index_2 = numpy.asarray(index_1), numpy.asarray(index_2)
        new = scipy.sparse.coo_array(
            (
                numpy.concatenate([weights, weights]),
                (
                    numpy.concatenate([index_1, index_2]),
                    numpy.concatenate([index_2, index_1]),
                ),
            ),
            shape=(n, n),
        ).tocsr()
        keep = self.matrix - self.matrix.multiply(new != 0)
        self.matrix = scipy.sparse.csr_array(keep + new)
        self.matrix.eliminate_zeros()
        self.matrix.sort_indices()

    # ==========================================================================
    # Nodes

    def number_of_nodes(self):
        return len(self.voxels_position)

    def number_of_edges(self):
        return self.matrix.nnz // 2

    def __len__(self):
        return self.number_of_nodes()

    def nodes(self):
        """List of the node positions, as 3-tuples, in node order."""
        if self._nodes is None:
            self._nodes = list(map(tuple, self.voxels_position.tolist()))
        return self._nodes

    def __iter__(self):
        return iter(self.nodes())

    def _node_index(self):
        if self._index is None:
            self._index = {node: i for i, node in enumerate(self.nodes())}
        return self._index

    def has_node(self, node):
        try:
            return tuple(node) in self._node_index()
        except TypeError:
            return False

    def __contains__(self, node):
        return self.has_node(node)

    def index(self, node):
        """Index of the node at position node (KeyError if absent)."""
        return self._node_index()[tuple(node)]

    def indices(self, positions):
        """Indices of the nodes at positions, -1 for absent positions."""
        index = self._node_index()
        positions = numpy.asarray(positions, dtype=float).reshape(-1, 3)
        return numpy.array(
            [index.get(p, -1) for p in map(tuple, positions.tolist())],
            dtype=numpy.int64,
        )

    def positions(self, indices):
        """Set of the positions (3-tuples) of the nodes indices."""
        nodes = self.nodes()
        return {nodes[i] for i in numpy.asarray(indices).tolist()}

    def neighbors(self, node):
        """List of the neighbor positions of the node at position node."""
        i = self.index(node)
        nodes = self.nodes()
        start, stop = self.matrix.indptr[i], self.matrix.indptr[i + 1]
        return [nodes[j] for j in self.matrix.indices[start:stop].tolist()]

    def subgraph(self, nodes):
        """VoxelGraph of the given node positions and the edges between them."""
        index = self.indices(list(nodes))
        index = numpy.unique(index[index >= 0])
        matrix = self.matrix[index][:, index]
        return VoxelGraph(self.voxels_position[index], self.voxels_size, matrix)
