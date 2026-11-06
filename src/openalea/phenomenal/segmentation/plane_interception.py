# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import math
import numpy

from ..object import VoxelGraph

import scipy
# ==============================================================================


def max_distance_in_points(points):
    """
    Compute and return the maximal Euclidean distance between the two point the
    most separate in points.

    Parameters
    ----------
    points: numpy.ndarray
        array of 3d points position.

    Returns
    -------
    max: int
        The maximal distance
    """
    if len(points) == 0:
        return 0

    result = scipy.spatial.distance.pdist(points, "euclidean")

    if len(result) > 0:
        return result.max()
    return 0


def max_distance_from_point_to_points(points, src_point):
    """
    Compute and return the maximal Euclidean distance between src_point and
    the most separate point from him in points.

    Parameters
    ----------
    src_point: tuple
        3-tuple position of src_points: (x, y, z)
    points: numpy.ndarray
        An ndarray of 3d points position.

    Returns
    -------
    max: int
        The maximal distance
    """
    if len(points) == 0:
        return 0

    result = scipy.spatial.distance.cdist(numpy.array([src_point]), points, "euclidean")

    if len(result) > 0:
        return result.max()
    return 0


def _as_voxel_graph(graph):
    if isinstance(graph, VoxelGraph):
        return graph
    return VoxelGraph.from_networkx(graph, None)


def _allowed_nodes(graph, points):
    """Boolean array over the graph nodes: True for the nodes at points."""
    if points is graph.voxels_position:
        return numpy.ones(graph.number_of_nodes(), dtype=bool)
    allowed = numpy.zeros(graph.number_of_nodes(), dtype=bool)
    index = graph.indices(points)
    allowed[index[index >= 0]] = True
    return allowed


def _walk_from_point(graph, src_point, accept, allowed):
    """Positions connected to src_point through accepted and allowed nodes,
    or [src_point] if src_point itself is not accepted or allowed."""
    if src_point not in graph:
        return [src_point]
    source = graph.index(src_point)
    if not allowed[source] or not accept(graph.voxels_position[[source]])[0]:
        return [src_point]
    return graph.positions(graph.walk(source, accept, allowed))


def connected_points_with_point(points, points_graph, src_point):
    """
    Return the connected points with src_point, based on points graph
    connection.

    src_point should be in the points_graph.

    Parameters
    ----------
    points: numpy.ndarray
        Points positions x, y, z
    src_point: numpy.ndarray
        Point position x, y, z
    points_graph: VoxelGraph or networkx.Graph
        The point graph

    Returns
    -------
    connected_points: set
        Return the connected points with src_point, based on points graph
        connection.
    """
    graph = _as_voxel_graph(points_graph)
    src_point = tuple(map(float, src_point))
    if len(points) == 0:
        return [src_point]
    allowed = _allowed_nodes(graph, numpy.asarray(list(points), dtype=float))
    return _walk_from_point(
        graph, src_point, lambda p: numpy.ones(len(p), dtype=bool), allowed
    )


def connected_voxel_with_point(voxels_point, voxels_size, src_voxel_point):
    """
    Return connected voxels point with src_voxel_point based on 26 neighboring
    voxel grid, with a size of voxels_size.

    .. warning:: WARNING ! Work only with connected voxel, and voxel grid

    Parameters
    ----------
    voxels_point: numpy.ndarray
        array of voxel grid point
    voxels_size: int
        the size of each voxel.
    src_voxel_point: tuple
        position x, y, z of voxel point

    Returns
    -------
    connected_voxels: list[tuple]
        A list of the connected voxels with the point.
    """
    closest_node, nodes = [], []
    nodes.append(numpy.array(src_voxel_point))
    while nodes:
        node = nodes.pop()
        rr = abs(voxels_point - node)

        index = numpy.where(
            (rr[:, 0] <= voxels_size)
            & (rr[:, 1] <= voxels_size)
            & (rr[:, 2] <= voxels_size)
        )[0]

        nodes += list(voxels_point[index])
        closest_node += list(voxels_point[index])

        voxels_point = numpy.delete(voxels_point, index, 0)

        if voxels_point.size == 0:
            break

    return list(map(tuple, closest_node))


def intercept_points_from_src_point_with_plane_equation(
    points, src_point, plane_equation, distance_from_plane, distance_from_src_point=None
):
    """
    Intercept the points who's the distance from the plane (generate by
    plane_equation) are equal or inferior to the distance_from_plane. If
    distance_from_src_point is not None, the intercept points are also the
    points who's the distance from the src_point are equal or inferior to the
    distance_from_src_point.

    If points_graph is not None, points return are the points in the same
    connected component that src_point.

    Parameters
    ----------
    points: numpy.ndarray
        Array containing x,y, z position of each point.
    src_point: tuple
        Point source.
    plane_equation: tuple
        Element of an equation
    distance_from_plane: float
        The maximum distance from a plane.
    distance_from_src_point: float
        The distance from the source point
    Returns
    -------
    closest_voxel: tuple
        the closest voxels.
    """
    res = abs(
        points[:, 0] * plane_equation[0]
        + points[:, 1] * plane_equation[1]
        + points[:, 2] * plane_equation[2]
        - plane_equation[3]
    ) / (
        math.sqrt(
            plane_equation[0] ** 2 + plane_equation[1] ** 2 + plane_equation[2] ** 2
        )
    )

    index = numpy.where(res < distance_from_plane)[0]
    closest_voxel = points[index]

    if distance_from_src_point is not None:
        res = numpy.linalg.norm(closest_voxel - src_point, axis=1)
        index = numpy.where(res < distance_from_src_point)[0]
        closest_voxel = closest_voxel[index]

    return closest_voxel


def _plane_test(src_point, plane_equation, distance_from_plane, distance_from_src_point):
    """Function selecting the positions as
    intercept_points_from_src_point_with_plane_equation, same operations."""
    a, b, c, d = plane_equation
    norm = math.sqrt(a**2 + b**2 + c**2)
    src = numpy.asarray(src_point, dtype=float)

    def accept(points):
        res = abs(points[:, 0] * a + points[:, 1] * b + points[:, 2] * c - d) / norm
        selected = res < distance_from_plane
        if distance_from_src_point is not None:
            selected &= numpy.linalg.norm(points - src, axis=1) < distance_from_src_point
        return selected

    return accept


def compute_plane_equation(orientation_vector, src_point):
    """
    Computation of plane equation
    x, y, z = src_point
    a, b, c, _ = k
    Plane equation : - d = a * x + b * y + c * z

    Parameters
    ----------

    orientation_vector: tuple
        The orientation vector.
    src_point: tuple
        The source point.

    Returns
    -------
    plane_equation: tuple
        The plane equation.
    """

    d = (
        orientation_vector[0] * src_point[0]
        + orientation_vector[1] * src_point[1]
        + orientation_vector[2] * src_point[2]
    )

    plane_equation = (
        orientation_vector[0],
        orientation_vector[1],
        orientation_vector[2],
        d,
    )

    return plane_equation


def orientation_vector_of_point_in_polyline(polyline, index_point, windows_size):
    """
    Compute and return orientation vector of point in polyline.

    Parameters
    ----------
    polyline: numpy.ndarray
        The polyline.
    index_point: int
        The index of the point.
    windows_size: int
        The size of the search window.

    Returns
    -------
    orientation_vector: tuple
        The orientation vector of the input point.
    """
    length_polyline = len(polyline)
    vectors = []
    for j in range(1, windows_size):
        x1, y1, z1 = polyline[max(0, index_point - j)]
        x2, y2, z2 = polyline[min(length_polyline - 1, index_point + j)]
        vectors.append((x2 - x1, y2 - y1, z2 - z1))

    orientation_vector = numpy.array(vectors).astype(float).mean(axis=0)

    return orientation_vector


def intercept_points_along_path_with_planes(
    points,
    polyline,
    windows_size=8,
    distance_from_plane=4,
    points_graph=None,
    without_connection=False,
    voxels_size=4,
    with_relative_distance=True,
    fix_distance_from_src_point=None,
):
    """
    Return a list of the intercept points along a path with a plane.

    Parameters
    ----------
    points: list
        The list of points.
    polyline: numpy.ndarray
        Array of points.
    windows_size: int
        The size of the search window.
    distance_from_plane: int
        The maximum distance from the plane.
    points_graph: VoxelGraph or networkx.Graph
        The point graph.
    without_connection: bool
        Whether the graph as connection or not.
    voxels_size: int
        The size of each voxel.
    with_relative_distance: bool
    fix_distance_from_src_point: float
        (optional) use a fixed distance.

    Returns
    -------
    out: tuple
        a tuple with a list of intercepted points and the plane equation.

    """
    length_polyline = len(polyline)
    intercepted_points = [None] * length_polyline
    planes_equation = [None] * length_polyline
    distance_from_src_point = (1000,)
    graph = allowed = None
    for i in range(length_polyline - 1, -1, -1):
        point = tuple(map(float, polyline[i]))

        # ======================================================================

        orientation_vector = orientation_vector_of_point_in_polyline(
            polyline, i, windows_size
        )

        plane_equation = compute_plane_equation(orientation_vector, point)

        if i < length_polyline - 1 and with_relative_distance:
            nodes = intercepted_points[i + 1]
            prev_radius_dist = max_distance_from_point_to_points(
                numpy.array(list(nodes)), polyline[i + 1]
            )

            if prev_radius_dist == 0:
                distance_from_src_point = 1000
            else:
                distance_from_src_point = min(
                    prev_radius_dist + 1 * voxels_size, 1000.0
                )

        if fix_distance_from_src_point is not None:
            distance_from_src_point = fix_distance_from_src_point

        # ======================================================================

        if points_graph is not None and not without_connection:
            # the points connected to point among the intercepted points:
            # walk the graph from point, testing only the points reached
            if graph is None:
                graph = _as_voxel_graph(points_graph)
                allowed = _allowed_nodes(graph, points)
            accept = _plane_test(
                point, plane_equation, distance_from_plane, distance_from_src_point
            )
            intercepted_points[i] = _walk_from_point(graph, point, accept, allowed)
            planes_equation[i] = plane_equation
            continue

        pts = intercept_points_from_src_point_with_plane_equation(
            points, point, plane_equation, distance_from_plane, distance_from_src_point
        )

        if without_connection:
            pts = list(map(tuple, pts))
        elif points_graph is not None:
            pts = list(map(tuple, pts))
            pts = connected_points_with_point(pts, points_graph, point)
        else:
            pts = connected_voxel_with_point(pts, voxels_size, point)

        intercepted_points[i] = pts
        planes_equation[i] = plane_equation

    return intercepted_points, planes_equation


def intercept_points_with_ball(points, ball_center, ball_radius):
    """
    Return a list of the intercept points by a ball of radius ball_radius and
    with center position ball_center.

    Parameters
    ----------
    points: numpy.ndarray
        Array of the x,y,z position of points.
    ball_center: tuple
        ndarray - position x, y, z of center position of the ball.
        Ball center position should be in the points graph.
    ball_radius: float
        Radius of the ball

    Returns
    -------
    points: list
        list of intercepted points
    """
    # Compute points in the ball
    points_distance_from_point = numpy.linalg.norm(points - ball_center, axis=1)
    index = numpy.where(points_distance_from_point < ball_radius)

    return points[index]


def intercept_points_along_polyline_with_ball(points, graph, polyline, ball_radius=50):
    """
    Return a list of intercept point along a polyline by a ball at each
    point.

    Parameters
    ----------
    points: numpy.ndarray
        Array of points
    polyline: numpy.ndarray
        Array of points
    graph: VoxelGraph or networkx.Graph
        Graph of the points
    ball_radius: float
        The radius of the ball in mm

    Returns
    -------
    intercepted_points: list
        list of points intercepted by the ball [[(x, y, z), ...], ...].
    """
    graph = _as_voxel_graph(graph)
    allowed = _allowed_nodes(graph, points)
    intercepted_points = []
    for point in polyline:
        center = numpy.asarray(point, dtype=float)

        def accept(positions):
            # same test as intercept_points_with_ball
            return numpy.linalg.norm(positions - center, axis=1) < ball_radius

        intercepted_points.append(
            _walk_from_point(graph, tuple(map(float, point)), accept, allowed)
        )

    return intercepted_points
