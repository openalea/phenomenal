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
import networkx

from alinea.phenomenal.data_structure import VoxelGraph
# ==============================================================================


def get_test_graph():

    voxels_size = 1
    graph = networkx.Graph()

    # nodes = [(0, 1, 0),
    #          (0, 0, 0),
    #          (1, 2, 0),
    #          (4, 8, 12)]
    #
    # graph.add_nodes_from(nodes)

    graph.add_edge((0, 1, 0), (0, 0, 0), weight=2)
    graph.add_edge((0, 1, 0), (4, 8, 12), weight=10)
    graph.add_edge((0, 1, 0), (1, 2, 0), weight=10)
    graph.add_edge((0, 0, 0), (1, 2, 0), weight=8)
    graph.add_edge((0, 0, 0), (4, 8, 12), weight=8)
    graph.add_edge((1, 2, 0), (4, 8, 12), weight=0)

    nodes = [(0, 1, 0),
             (0, 0, 0),
             (1, 2, 0),
             (4, 8, 12)]

    graph.add_nodes_from(nodes)

    return VoxelGraph(graph, voxels_size)


def test_read_write():

    vg = get_test_graph()


# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
