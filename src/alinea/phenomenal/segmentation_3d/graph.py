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
# ==============================================================================


def create_graph(voxel_centers, voxel_size=1):

    graph = networkx.Graph()
    graph.add_nodes_from(voxel_centers)

    vs = voxel_size
    ijk = [(-vs, -vs, -vs),
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
           (0, 0, 0),
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
           (vs, vs, vs)]

    for pt in voxel_centers:
        for i, j, k in ijk:
            pos = pt[0] + i, pt[1] + j, pt[2] + k
            if graph.has_node(pos):
                d = numpy.linalg.norm(numpy.array(pt) - numpy.array(pos))
                graph.add_edge(pt, pos, weight=d)
                # graph.add_edge(pt, pos, weight=abs(i) + abs(j) + abs(k))

    return graph


def add_nodes(graph, voxel_centers, voxel_size=1):

    graph.add_nodes_from(voxel_centers)

    vs = voxel_size
    ijk = [(-vs, -vs, -vs), (-vs, -vs, 0), (-vs, -vs, vs),
           (-vs, 0, -vs), (-vs, 0, 0), (-vs, 0, vs),
           (-vs, vs, -vs), (-vs, vs, 0), (-vs, vs, vs),
           (0, -vs, -vs), (0, -vs, 0), (0, -vs, vs),
           (0, 0, -vs), (0, 0, 0), (0, 0, vs),
           (0, vs, -vs), (0, vs, 0), (0, vs, vs),
           (vs, -vs, -vs), (vs, -vs, 0), (vs, -vs, vs),
           (vs, 0, -vs), (vs, 0, 0), (vs, 0, vs),
           (vs, vs, -vs), (vs, vs, 0), (vs, vs, vs)]

    for pt in voxel_centers:
        for i, j, k in ijk:
            pos = pt[0] + i, pt[1] + j, pt[2] + k
            if graph.has_node(pos):
                d = numpy.linalg.norm(numpy.array(pt) - numpy.array(pos))
                graph.add_edge(pt, pos, weight=d)
                # graph.add_edge(pt, pos, weight=abs(i) + abs(j) + abs(k))

    return graph
