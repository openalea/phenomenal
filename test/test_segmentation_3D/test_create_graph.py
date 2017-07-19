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
import time

from alinea.phenomenal.segmentation_3d import (
    voxel_graph_from_voxel_point_cloud)

from alinea.phenomenal.data_access import (
    plant_1_voxel_point_cloud)

from alinea.phenomenal.segmentation_3d import create_graph
# ==============================================================================


def test_time_graph():

    voxels_size = 16
    vpc = plant_1_voxel_point_cloud(voxels_size=voxels_size)
    number_of_loop = 2
    best_time = float('inf')
    for i in range(number_of_loop):
        t0 = time.time()
        graph = create_graph(vpc.voxels_position, vpc.voxels_size)
        best_time = min(best_time, float(time.time() - t0))

    print("{number_of_loop} loop, best of {number_of_loop}: "
          "{best_time}s per loop".format(best_time=best_time,
                                         number_of_loop=number_of_loop))


def test_graph_1():

    voxels_position = [(0, 0, 0),
                       (0, 0, 1),
                       (0, 1, 0),
                       (1, 1, 1),
                       (1, 1, 2),
                       (2, 1, 2),
                       (1, 2, 1),
                       (2, 2, 2),
                       (5, 5, 5)]

    voxels_size = 1
    graph = create_graph(voxels_position, voxels_size=voxels_size)

    print("Number of nodes : {nb_nodes}".format(nb_nodes=len(graph.nodes())))

    assert len(voxels_position) == len(graph.nodes())

    for position in voxels_position:
        assert graph.has_node(position)

    l = networkx.dijkstra_path_length(graph,
                                      source=(0, 0, 0),
                                      target=(2, 2, 2),
                                      weight="weight")

    ll = numpy.linalg.norm(numpy.array((0, 0, 0)) - numpy.array((2, 2, 2)))

    assert l == ll

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()