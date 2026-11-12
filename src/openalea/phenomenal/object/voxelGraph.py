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

import itertools

import numpy
import scipy.sparse
import scipy.sparse.csgraph
import scipy.spatial

# ==============================================================================


class VoxelGraph:
    """Weighted undirected graph of voxel centers.

    Each node is a voxel center position (a 3-tuple). Nodes are also numbered
    0..N-1, in the order of voxels_position. Edges are stored in matrix, a
    symmetric scipy sparse matrix of the edge weights (distances).

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
        self._state = None

    # ==========================================================================
    # Construction

    @classmethod
    def from_voxels_position(cls, voxels_position, voxels_size):
        """Graph where each voxel is connected to its 26 neighbors.

        A voxel is a neighbor if its position is exactly the voxel position
        plus a combination of -voxels_size, 0, voxels_size on each axis. The
        edge weight is the distance between the two voxel centers.
        """
        positions = numpy.asarray(voxels_position, dtype=float).reshape(-1, 3)
        n = len(positions)
        if n == 0:
            return cls(positions, voxels_size)

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
        return cls(positions, voxels_size, matrix)

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

    # ==========================================================================
    # Algorithms

    def connected_components_labels(self):
        """Number of connected components, and component label of each node."""
        return scipy.sparse.csgraph.connected_components(self.matrix, directed=False)

    def connected_components(self):
        """List of the connected components, as sets of node positions."""
        n, labels = self.connected_components_labels()
        order = numpy.argsort(labels, kind="stable")
        bounds = numpy.cumsum(numpy.bincount(labels, minlength=n))[:-1]
        return [self.positions(group) for group in numpy.split(order, bounds)]

    def number_connected_components(self):
        return self.connected_components_labels()[0]

    def connect_components(self):
        """Connect all the connected components together, in place.

        Starting from the largest component, the closest component is
        connected by an edge between its two closest nodes, until there is
        one component. Returns the graph.
        """
        n, labels = self.connected_components_labels()
        if n <= 1:
            return self
        positions = self.voxels_position
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
        self.add_edges(index_1, index_2, numpy.array(weights))
        return self

    def shortest_paths_tree(self, source):
        """Shortest paths (Dijkstra) from the node index source.

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
            self.matrix, directed=False, indices=source, return_predecessors=True
        )
        lengths = numpy.zeros(len(distances), dtype=numpy.int64)
        lengths[source] = 1
        reachable = numpy.flatnonzero(numpy.isfinite(distances))
        # a predecessor is always closer to source than its successor
        for i in reachable[numpy.argsort(distances[reachable], kind="stable")].tolist():
            if i != source:
                lengths[i] = lengths[predecessors[i]] + 1
        return predecessors, lengths

    @staticmethod
    def path(predecessors, target):
        """Node indices of the path ending at target, from the source."""
        path = [target]
        while predecessors[path[-1]] >= 0:
            path.append(int(predecessors[path[-1]]))
        return path[::-1]

    def walk(self, source, accept, allowed=None):
        """Nodes connected to source through accepted nodes.

        Parameters
        ----------
        source : int
            Index of the start node. It must be accepted.
        accept : callable
            accept(positions) returns a boolean array: True for the positions
            (array (k, 3)) of the nodes that the walk can go through.
        allowed : numpy.ndarray, optional
            Boolean array over the nodes: the walk only goes through allowed
            nodes.

        Returns
        -------
        indices : numpy.ndarray
            Indices of the connected nodes, source included.
        """
        if self._state is None or len(self._state) != self.number_of_nodes():
            self._state = numpy.zeros(self.number_of_nodes(), dtype=bool)
        seen = self._state
        indptr, indices = self.matrix.indptr, self.matrix.indices
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
            frontier = candidates[accept(self.voxels_position[candidates])]
            connected.append(frontier)
        seen[numpy.concatenate(touched)] = False
        return numpy.concatenate(connected)
