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
import scipy

from alinea.phenomenal.data_structure.voxelGraph import VoxelGraph
# ==============================================================================


def voxel_graph_from_voxel_point_cloud(voxel_point_cloud,
                                       connect_all_point=True):
    voxels_size = voxel_point_cloud.voxels_size
    voxels_position = voxel_point_cloud.voxels_position

    # ==========================================================================
    # Graph creation
    graph = create_graph(voxels_position, voxels_size=voxels_size)

    if connect_all_point:
        graph = connect_all_node_with_nearest_neighbors(graph)
    else:
        # Keep the biggest connected components
        graph = max(networkx.connected_component_subgraphs(graph, copy=False),
                    key=len)
    return VoxelGraph(graph, voxels_size)


def connect_all_node_with_nearest_neighbors(graph):

    connected_component = list(networkx.connected_component_subgraphs(
        graph, copy=False))

    nodes_connected_component = [cc.nodes() for cc in connected_component]

    while len(nodes_connected_component) > 1:

        nodes_src = nodes_connected_component[0]
        nodes_dst = set()
        nodes_connected_component = nodes_connected_component[1:]

        pt1 = None
        pt2 = None
        min_dist = float('inf')

        for nodes in nodes_connected_component:

            result = scipy.spatial.distance.cdist(nodes_src, nodes, 'euclidean')

            min1 = result.min(axis=1)
            m = min1.min(axis=0)

            if m < min_dist:
                min_dist = m

                dst_index = numpy.argmin(result, axis=1)
                src_index = numpy.argmin(min1, axis=0)

                pt1 = nodes_src[src_index]
                pt2 = nodes[dst_index[src_index]]

                nodes_dst = nodes

        nodes_connected_component.remove(nodes_dst)
        nodes_connected_component.append(list(set(nodes_src).union(nodes_dst)))
        graph.add_edge(pt1, pt2, weight=min_dist)

    return graph


def create_graph(voxels_position, voxels_size=1):

    graph = networkx.Graph()
    graph.add_nodes_from(voxels_position)

    vs = voxels_size
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

    for pt in voxels_position:
        for i, j, k in ijk:
            pos = pt[0] + i, pt[1] + j, pt[2] + k
            if graph.has_node(pos):
                d = numpy.linalg.norm(numpy.array(pt) - numpy.array(pos))
                graph.add_edge(pt, pos, weight=d)

    return graph


def add_nodes(graph, voxels_position, voxels_size=1):

    graph.add_nodes_from(voxels_position)

    vs = voxels_size
    ijk = [(-vs, -vs, -vs), (-vs, -vs, 0), (-vs, -vs, vs),
           (-vs, 0, -vs), (-vs, 0, 0), (-vs, 0, vs),
           (-vs, vs, -vs), (-vs, vs, 0), (-vs, vs, vs),
           (0, -vs, -vs), (0, -vs, 0), (0, -vs, vs),
           (0, 0, -vs), (0, 0, 0), (0, 0, vs),
           (0, vs, -vs), (0, vs, 0), (0, vs, vs),
           (vs, -vs, -vs), (vs, -vs, 0), (vs, -vs, vs),
           (vs, 0, -vs), (vs, 0, 0), (vs, 0, vs),
           (vs, vs, -vs), (vs, vs, 0), (vs, vs, vs)]

    for pt in voxels_position:
        for i, j, k in ijk:
            pos = pt[0] + i, pt[1] + j, pt[2] + k
            if graph.has_node(pos):
                d = numpy.linalg.norm(numpy.array(pt) - numpy.array(pos))
                graph.add_edge(pt, pos, weight=d)

    return graph
