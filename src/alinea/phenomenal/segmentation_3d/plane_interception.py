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
import math
import numpy
import networkx
import scipy

# ==============================================================================

def get_length_point_cloud(nodes):
    if len(nodes) == 0:
        return 0

    res = scipy.spatial.distance.pdist(nodes, 'euclidean')

    if len(res) > 0:
        return res.max()
    else:
        return 0


def get_node_close_to_planes(voxels, node_src, plane,
                             dist=0.75,
                             radius_dist=None,
                             voxels_size=8,
                             graph=None,
                             without_connexity=False):
    """
    - voxels is a numpy array
    - node_src tuple
    - plane is a tuple of 4 elements containing (a, b, c, d) value of a plane
    equation

    - dist : is the maximal distance between plane and node

    """

    # TODO : Maybe change that by graph connected definition

    res = abs(voxels[:, 0] * plane[0] +
              voxels[:, 1] * plane[1] +
              voxels[:, 2] * plane[2] -
              plane[3]) / (math.sqrt(plane[0] ** 2 +
                                     plane[1] ** 2 +
                                     plane[2] ** 2))

    index = numpy.where(res < dist)[0]
    closest_voxel = voxels[index]

    if without_connexity:
        return map(tuple, closest_voxel)

    if radius_dist is not None:
        res = numpy.linalg.norm(closest_voxel - node_src, axis=1)
        index = numpy.where(res < radius_dist)[0]
        closest_voxel = closest_voxel[index]

    nodes = list()
    closest_node = list()

    if graph is not None:
        closest_voxel = map(tuple, closest_voxel)

        subgraph = graph.subgraph(closest_voxel)
        connected_component = networkx.connected_components(
            subgraph)

        for cc in connected_component:
            if node_src in cc:
                return cc

    nodes.append(numpy.array(node_src))

    while nodes:
        node = nodes.pop()

        rr = abs(closest_voxel - node)

        index = numpy.where((rr[:, 0] <= voxels_size) &
                            (rr[:, 1] <= voxels_size) &
                            (rr[:, 2] <= voxels_size))[0]

        nodes += list(closest_voxel[index])
        closest_node += list(closest_voxel[index])

        closest_voxel = numpy.delete(closest_voxel, index, 0)

        if closest_voxel.size == 0:
            break

    return map(tuple, closest_node)


def compute_closest_nodes_with_planes(voxels, path, radius=8, dist=1.00,
                                      radius_dist=None,
                                      graph=None,
                                      without_connexity=False,
                                      voxels_size=4):

    closest_nodes = list()
    length_path = len(path)

    # radius_dist = 100
    b = False
    for i in range(length_path):
        node = tuple(path[i])

        # ======================================================================

        vectors = list()
        for j in range(1, radius):
            x, y, z = path[max(0, i - j)]
            xx, yy, zz = path[min(length_path - 1, i + j)]

            v = map(float, (xx - x, yy - y, zz - z))
            vectors.append(v)

        vector_mean = numpy.array(vectors).mean(axis=0)

        k = vector_mean

        # ======================================================================

        # Computation of plane equation
        # x, y, z = node
        # a, b, c, _ = k
        # Plane equation : d = a * x + b * y + c * z
        d = k[0] * node[0] + k[1] * node[1] + k[2] * node[2]
        plane = (k[0], k[1], k[2], d)

        # if i > 0:
        #     nodes = closest_nodes[i - 1]
        #     distance = get_length_point_cloud(numpy.array(list(nodes)))
        #     if distance == 0:
        #         radius_dist = 100
        #     else:
        #         radius_dist = min(distance * 1.5, 100)
        #

        nodes = get_node_close_to_planes(voxels, node, plane,
                                         dist=dist,
                                         graph=graph,
                                         radius_dist=radius_dist,
                                         without_connexity=without_connexity,
                                         voxels_size=voxels_size)

        closest_nodes.append(nodes)

        if b is True:
            import alinea.phenomenal.display

            alinea.phenomenal.display.show_list_voxels(
                [voxels, nodes, path],
                [voxels_size * 0.75, voxels_size * 0.75, voxels_size * 0.75],
                [(0, 0, 0), (0, 0, 1), (1, 0, 0)])


    return closest_nodes


def compute_closest_nodes_with_ball(voxels, path, ball_radius=50, graph=None):

    closest_nodes = list()
    path = numpy.array(path)
    for i, node in enumerate(path):

        res = numpy.linalg.norm(voxels - node, axis=1)
        index = numpy.where(res < ball_radius)
        nodes = voxels[index]

        if graph is not None:
            closest_voxel = map(tuple, nodes)
            subgraph = graph.subgraph(closest_voxel)
            connected_component = networkx.connected_component_subgraphs(
                subgraph, copy=False)

            for cc in connected_component:
                if node in cc:
                    nodes = cc

        closest_nodes.append(map(tuple, nodes))

    return closest_nodes
