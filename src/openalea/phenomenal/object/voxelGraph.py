# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import os
import json
import networkx
import numpy
import scipy.sparse

from networkx.readwrite.graphml import (read_graphml, write_graphml)
from networkx.readwrite.json_graph import (node_link_data, node_link_graph)
# ==============================================================================


class VoxelGraph(object):

    def __init__(self, graph, voxels_size):
        self.graph = graph
        self.voxels_size = voxels_size

    # ==========================================================================
    # READ / WRITE
    # ==========================================================================

    def write_to_npz(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        nodes = self.graph.nodes()
        matrix = networkx.to_scipy_sparse_matrix(self.graph)

        numpy.savez_compressed(filename,
                               data=matrix.data,
                               indices=matrix.indices,
                               indptr=matrix.indptr,
                               shape=matrix.shape,
                               nodes=nodes,
                               voxels_size=self.voxels_size,
                               allow_pickle=False)

    def write_to_gml(self, filename):

        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        networkx.write_gml(self.graph, filename)

    @staticmethod
    def read_from_gml(filename, voxels_size):
        graph = networkx.read_gml(filename)

        VoxelGraph(graph, voxels_size)

    def write_to_graphml(self, filename):
        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        write_graphml(self.graph, filename)

    @staticmethod
    def read_from_graphml(filename, voxels_size):
        graph = read_graphml(filename, node_type=tuple)

        return VoxelGraph(graph, voxels_size)

    def write_to_json(self, filename):
        if (os.path.dirname(filename) and not os.path.exists(
                os.path.dirname(filename))):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as f:

            data = dict()
            data['graph'] = node_link_data(self.graph)
            data['voxels_size'] = self.voxels_size
            json.dump(data, f)

    @staticmethod
    def read_from_json(filename):

        with open(filename, 'rb') as f:

            data = json.load(f)

            data_graph = data['graph']
            for node in data_graph['nodes']:
                node['id'] = tuple(node['id'])

            graph = node_link_graph(data_graph)
            voxels_size = data['voxels_size']

            return VoxelGraph(graph, voxels_size)
