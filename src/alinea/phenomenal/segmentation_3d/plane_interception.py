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
import collections
import time
# ==============================================================================


def get_node_close_to_planes(voxels, node_src, plane, dist=0.75):
    """
    - voxels is a numpy array
    - node_src tuple
    - plane is a tuple of 4 elements containing (a, b, c, d) value of a plane
    equation

    - dist : is the maximal distance between plane and node

    """

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

    # if node_src in map(tuple, voxels):
    nodes.append(numpy.array(node_src))
    closest_node.append(numpy.array(node_src))

    while nodes:
        node = nodes.pop()

        rr = numpy.sum(abs(closest_voxel - node), 1)

        index = numpy.where(rr <= 3)[0]
        nodes += list(closest_voxel[index])
        closest_node += list(closest_voxel[index])

        closest_voxel = numpy.delete(closest_voxel, index, 0)

        if closest_voxel.size == 0:
            break

    return map(tuple, closest_node)


def compute_closest_nodes(voxels, path, radius=8, dist=0.75):
    planes = list()
    closest_nodes = list()

    length_path = len(path)
    for i in xrange(length_path):
        node = path[i]

        neighbors = numpy.array(
            path[max(0, i - radius):min(length_path, i + radius)])

        # Do an SVD on the mean-centered neighbors points.
        k = abs(numpy.linalg.svd(neighbors - neighbors.mean(axis=0))[2][0])

        # Computation of plane equation
        # x, y, z = node
        # a, b, c, _ = k
        # Plane equation : d = a * x + b * y + c * z
        d = k[0] * node[0] + k[1] * node[1] + k[2] * node[2]
        plane = (k[0], k[1], k[2], d)

        planes.append(plane)

        nodes = get_node_close_to_planes(voxels, node, plane, dist=dist)
        closest_nodes.append(nodes)

    return planes, closest_nodes

# ==============================================================================
# Old implementation soon removed TODO: remove below or move for visualization
# ==============================================================================

def compute_planes(points):
    mean_point = points.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = numpy.linalg.svd(points - mean_point)

    return vv[0]


def get_point_of_planes(normal, node, radius=5):
    a, b, c = normal
    x, y, z = node

    d = a * x + b * y + c * z

    xx = numpy.linspace(x - radius, x + radius, radius * 2)
    yy = numpy.linspace(y - radius, y + radius, radius * 2)

    xv, yv = numpy.meshgrid(xx, yy)

    zz = - (a * xv + b * yv - d) / c

    return xv, yv, zz


def get_distance_point_to_plane(node, plane):
    x, y, z = node
    a, b, c, d = plane

    return abs(a * x + b * y + c * z - d) / math.sqrt(a ** 2 + b ** 2 + c ** 2)


def get_node_close_to_planes_2(graph, node_src, plane, dist=0.75):
    a, b, c, d = plane
    plane_square = math.sqrt(a ** 2 + b ** 2 + c ** 2)

    closest_node = list()
    closest_node.append(node_src)

    nodes = collections.deque()
    nodes += graph[node_src].keys()
    while nodes:
        node = nodes.pop()

        if node not in closest_node:
            x, y, z = node

            # Plane distance equation
            distance = abs(a * x + b * y + c * z - d) / plane_square

            if distance < dist:
                closest_node.append(node)

                nodes += graph[node].keys()

    return closest_node


def compute_closest_nodes_2(graph, path, radius=8, verbose=False, dist=0.75):
    if verbose:
        print "Computation of planes long to the path : ...",
        t0 = time.time()

    planes = list()
    closest_nodes = list()
    centred_path = list()

    length_path = len(path)
    for i in xrange(length_path):
        node = path[i]

        neighbors = numpy.array(
            path[max(0, i - radius):min(length_path, i + radius)])

        # Do an SVD on the mean-centered neighbors points.
        k = numpy.linalg.svd(neighbors - neighbors.mean(axis=0))[2][0]

        # Computation of plane equation
        # x, y, z = node
        # a, b, c, _ = k
        # Plane equation : d = a * x + b * y + c * z
        d = k[0] * node[0] + k[1] * node[1] + k[2] * node[2]
        plane = (k[0], k[1], k[2], d)
        planes.append(plane)

        nodes = get_node_close_to_planes_2(graph, node, plane, dist=dist)

        centred_path.append(numpy.array(nodes).mean(axis=0))
        closest_nodes.append(nodes)

    if verbose:
        print "done, in ", time.time() - t0, 'seconds'

    return planes, closest_nodes, centred_path

