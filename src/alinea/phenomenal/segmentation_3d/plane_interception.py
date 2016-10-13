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

# ==============================================================================


def get_node_close_to_planes(voxels, node_src, plane, dist=0.75,
                             voxel_size=4, graph=None):
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

    nodes = list()
    closest_node = list()

    if graph is not None:
        closest_voxel = map(tuple, closest_voxel)
        subgraph = graph.subgraph(closest_voxel)
        connected_component = networkx.connected_component_subgraphs(
            subgraph, copy=False)

        for cc in connected_component:
            if node_src in cc:
                return cc

    nodes.append(numpy.array(node_src))

    while nodes:
        node = nodes.pop()

        rr = abs(closest_voxel - node)

        index = numpy.where((rr[:, 0] <= voxel_size) &
                            (rr[:, 1] <= voxel_size) &
                            (rr[:, 2] <= voxel_size))[0]

        nodes += list(closest_voxel[index])
        closest_node += list(closest_voxel[index])

        closest_voxel = numpy.delete(closest_voxel, index, 0)

        if closest_voxel.size == 0:
            break

    return map(tuple, closest_node)


def compute_closest_nodes(voxels, path, radius=8, dist=0.75, graph=None):
    planes = list()
    closest_nodes = list()

    length_path = len(path)
    for i in range(length_path):
        node = path[i]

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

        planes.append(plane)

        nodes = get_node_close_to_planes(voxels, node, plane, dist=dist,
                                         graph=graph)

        closest_nodes.append(nodes)

    return planes, closest_nodes
