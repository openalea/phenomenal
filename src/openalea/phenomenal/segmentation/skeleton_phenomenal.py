# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import numpy

try:
    import nx_cugraph as networkx
except ImportError:
    import networkx


from ..multi_view_reconstruction import get_bounding_box_voxel_projected
from .plane_interception import (
    intercept_points_along_path_with_planes,
    intercept_points_along_polyline_with_ball,
)
from ..object import VoxelSkeleton, VoxelGrid, VoxelSegment


# ==============================================================================


def _project_voxels_on_pixels(voxels_position, voxels_size, shape_image, projection):
    """
    Give the pixels covered by the voxels projected on an image, as flat indices.

    Covers the same pixels as `project_voxel_centers_on_image`, without allocating an
    image of the full size.

    Parameters
    ----------
    voxels_position : numpy.ndarray
        Voxels center position [[x, y, z], ...]
    voxels_size : float
        Diameter size of the voxels
    shape_image : 2-tuple
        Height and width of the image
    projection : function ((x, y, z)) -> (x, y)
        Function of projection

    Returns
    -------
    out : numpy.ndarray
        Sorted indices of the pixels in the flattened image
    """
    height, length = shape_image
    boxes = get_bounding_box_voxel_projected(voxels_position, voxels_size, projection)
    outside = (
        (boxes[:, 2] < 0)
        | (boxes[:, 0] >= length)
        | (boxes[:, 3] < 0)
        | (boxes[:, 1] >= height)
    )
    boxes = numpy.floor(boxes[~outside])
    if len(boxes) == 0:
        return numpy.empty(0, dtype=numpy.intp)

    boxes[:, [0, 2]] = numpy.clip(boxes[:, [0, 2]], 0, length - 1)
    boxes[:, [1, 3]] = numpy.clip(boxes[:, [1, 3]], 0, height - 1)
    boxes = boxes.astype(int)

    x_origin, y_origin = boxes[:, :2].min(axis=0)
    x_end, y_end = boxes[:, 2:].max(axis=0)
    crop = numpy.zeros((y_end - y_origin + 1, x_end - x_origin + 1), dtype=bool)
    for x_min, y_min, x_max, y_max in boxes - [x_origin, y_origin, x_origin, y_origin]:
        crop[y_min : y_max + 1, x_min : x_max + 1] = True

    rows, columns = numpy.nonzero(crop)
    return (rows + y_origin) * length + columns + x_origin


def segment_reduction(
    voxel_skeleton, image_projection, required_visible=4, nb_min_pixel=100
):
    """
    Reduce the number of segments in a VoxelSkeleton object, according to
    their projection results. Each segment is kept if their projection on
    the images are not cover by the projection of the other segments in
    number required_visible. Segments are not cover if their remaining
    projected pixel are superior to nb_min_pixel.

    Segments are processed from the shortest to the longest polyline, and a removed
    segment no longer covers the following ones.

    Parameters
    ----------
    voxel_skeleton : VoxelSkeleton
    image_projection : list of tuple (image, projection)
    required_visible : int, optional
        Number of required  not_covered segment to kept it.
    nb_min_pixel : int, optional
        Number of remaining pixel required to consider segment not covered
    Returns
    -------

    """
    segments = sorted(voxel_skeleton.segments, key=lambda vs: len(vs.polyline))

    # Number of objects covering each pixel of each image: the background, then the
    # projection of each remaining segment.
    coverages = [
        (image.astype(numpy.int32) == 0).astype(numpy.int32).ravel()
        for image, _ in image_projection
    ]
    segments_pixels = []
    for segment in segments:
        voxels_position = numpy.array(list(segment.voxels_position))
        pixels = [
            _project_voxels_on_pixels(
                voxels_position, voxel_skeleton.voxels_size, image.shape, projection
            )
            for image, projection in image_projection
        ]
        for coverage, pixels_in_image in zip(coverages, pixels):
            coverage[pixels_in_image] += 1
        segments_pixels.append(pixels)

    kept_segments = []
    for segment, pixels in zip(segments, segments_pixels):
        nb_visible = sum(
            numpy.count_nonzero(coverage[pixels_in_image] == 1)
            >= max(nb_min_pixel, 1)
            for coverage, pixels_in_image in zip(coverages, pixels)
        )
        if nb_visible < required_visible:
            for coverage, pixels_in_image in zip(coverages, pixels):
                coverage[pixels_in_image] -= 1
        else:
            kept_segments.append(segment)

    return VoxelSkeleton(kept_segments, voxel_skeleton.voxels_size)


# ==============================================================================


def _get_longest_shortest_path_in_nodes(nodes, paths):
    leaf_skeleton_path = None
    longest_length = 0
    for node in nodes:
        p = paths[node]

        if len(p) > longest_length:
            longest_length = len(p)
            leaf_skeleton_path = p

    return leaf_skeleton_path


def _segment_path(
    voxels,
    array_voxels,
    skeleton_path,
    graph,
    voxels_size=4,
    mode="plane",
    plane_width=4,
    ball_radius=10,
):
    # ==========================================================================
    # Get the longest shorted path of voxels
    polyline = _get_longest_shortest_path_in_nodes(voxels, skeleton_path)

    # ==========================================================================

    if polyline:
        if mode == "ball":
            intercept_points = intercept_points_along_polyline_with_ball(
                array_voxels, graph, polyline, ball_radius=ball_radius
            )
        else:
            intercept_points, _ = intercept_points_along_path_with_planes(
                array_voxels,
                polyline,
                distance_from_plane=plane_width,
                points_graph=graph,
                voxels_size=voxels_size,
            )

        voxels_position = set().union(*intercept_points)

        segment = VoxelSegment(polyline, voxels_position, intercept_points)

        remain = set(voxels).difference(segment.voxels_position)

        return segment, remain
    return None, None


def find_base_stem_position(voxels_position, voxels_size, neighbor_size=45):
    """Function to find the base stem position of the plant from the voxels
    center positions list.

    Voxels position are converted in 3d image to find around the x and y-axis
    the points with the minimum value in a range of neighbor_side.

    Parameters
    ----------
    voxels_position : ndarray
        3d voxels center positions [(x, y, z), ...]

    voxels_size : int
        Voxel size diameter

    neighbor_size : int, optional
        Radius size in mm to search the base stem position

    Returns
    -------
    base_stem_position : 3-tuple
    """
    image_3d = VoxelGrid(voxels_position, voxels_size).image_3d

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxels_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxels_size))

    k = neighbor_size / voxels_size

    x_len, y_len, _ = image_3d.shape

    roi = image_3d[
        int(max(x - k, 0)) : int(min(x + k, x_len)),
        int(max(y - k, 0)) : int(min(y + k, y_len)),
        :,
    ]

    xx, yy, zz = numpy.where(roi == 1)

    min_z_value = numpy.min(zz)
    index_min_z_value = numpy.where(zz == min_z_value)
    mean_float_point = numpy.array(
        [
            numpy.mean(xx[index_min_z_value]),
            numpy.mean(yy[index_min_z_value]),
            numpy.mean(zz[index_min_z_value]),
        ]
    )

    mean_point = None
    min_dist = float("inf")
    for xxx, yyy, zzz in zip(xx, yy, zz):
        pt = numpy.array([xxx, yyy, zzz])
        dist = numpy.linalg.norm(mean_float_point - pt)
        if dist < min_dist:
            min_dist = dist
            mean_point = pt

    stem_base_position = (
        int(max(x - k, 0)) + mean_point[0],
        int(max(y - k, 0)) + mean_point[1],
        mean_point[2],
    )

    base_stem_position = (
        numpy.array(stem_base_position) * voxels_size + image_3d.world_coordinate
    )

    return base_stem_position


def compute_all_shorted_path(graph, voxels_size, neighbor_size=45, src_node=None):
    """Compute all the shorted path from the base position of the graph
    position.

    Parameters
    ----------
    graph : networkx.Graph
        Graph of 3d voxel center point position

    voxels_size : int
        Voxels diameter size

    Returns
    -------
    all_shorted_path_to_stem_base : dict
        List of all the shorted path of the graph from the base
    """
    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    if src_node is None:
        x_stem, y_stem, z_stem = find_base_stem_position(
        graph.nodes(), voxels_size, neighbor_size=neighbor_size
        )
        src_node = (x_stem, y_stem, z_stem)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, src_node, weight="weight"
    )

    return all_shorted_path_to_stem_base


def skeletonize(
    voxel_grid,
    graph,
    subgraph=None,
    voxels_position_remain=None,
    mode="plane",
    plane_width=None,
    ball_radius=None,
    neighbor_size=45,
    src_node=None
):
    """Compute phenomenal skeletonization on the voxel_grid based on the graph.

    Parameters
    ----------
    voxel_grid : VoxelGrid

    graph : networkx.Graph

    subgraph: networkx.graph, optional
        If not None, perform the computation of the shorted paths on the
        subgraph and remove voxels

    mode : str, optional
        Mode for intercept point along the paths. Two mode available, "ball"
        or "plane". By default, "plane" mode.

    plane_width : int, optional
        Size in mm of the width of the plane. By default, or if None is equal
        to the voxel_size of the voxel_grid

    ball_radius : int, optional
        Size in mm of the radius of the ball. By default, or if None is equal
        to the voxel_size * 4 of the voxel_grid

    Returns
    -------
    voxel_skeleton : VoxelSkeleton
    """
    if plane_width is None:
        plane_width = voxel_grid.voxels_size * 2

    if ball_radius is None:
        ball_radius = voxel_grid.voxels_size * 4

    if subgraph is None:
        subgraph = graph

    voxels_size = voxel_grid.voxels_size
    all_shorted_path_to_stem_base = compute_all_shorted_path(
        subgraph, voxels_size, neighbor_size=neighbor_size,
        src_node=src_node
    )

    # ==========================================================================
    if voxels_position_remain is None:
        voxels_position_remain = subgraph.nodes()

    np_arr_all_graph_voxels_plant = numpy.array(graph.nodes())
    # ==========================================================================

    segments = []
    while len(voxels_position_remain) != 0:
        (voxel_segment, voxels_position_remain) = _segment_path(
            voxels_position_remain,
            np_arr_all_graph_voxels_plant,
            all_shorted_path_to_stem_base,
            graph,
            voxels_size=voxels_size,
            mode=mode,
            plane_width=plane_width,
            ball_radius=ball_radius,
        )

        segments.append(voxel_segment)

    return VoxelSkeleton(segments, voxels_size)
