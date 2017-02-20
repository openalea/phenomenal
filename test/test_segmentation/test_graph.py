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
import numpy

from alinea.phenomenal.segmentation_3d import create_graph
# ==============================================================================

def test_graph_1():

    pos_1, pos_2, pos_3, pos_4 = (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 1)
    pos_5, pos_6, pos_7, pos_8 = (1, 1, 2), (2, 1, 2), (1, 2, 1), (2, 2, 2)
    voxels_position = [pos_1, pos_2, pos_3, pos_4, pos_5, pos_6, pos_7, pos_8]

    voxels_size = 1
    graph = create_graph(voxels_position, voxels_size=voxels_size)

    # all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
    #     graph, (0, 0, 0), weight="weight")
    #
    # print all_shorted_path_to_stem_base

    l = networkx.dijkstra_path_length(graph,
                                      source=pos_1,
                                      target=pos_4,
                                      weight="weight")

    ll = numpy.linalg.norm(numpy.array(pos_1) - numpy.array(pos_4))

    assert l == ll

if __name__ == "__main__":
    test_graph_1()
