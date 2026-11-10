# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import os

import numpy

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.segmentation as phm_seg
from openalea.phenomenal.multi_view_reconstruction import (
    project_voxel_centers_on_image,
)
from openalea.phenomenal.object import VoxelSkeleton
from openalea.phenomenal.segmentation.skeleton_phenomenal import (
    _project_voxels_on_pixels,
)

from pathlib import Path
test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir.parent / "data" / "plant_1"

# ==============================================================================


def test_running():
    bin_images = phm_data.bin_images(data_dir)
    calibration = phm_data.load_calibration(data_dir)
    voxel_grid = phm_data.voxel_grid(data_dir, 32)

    # Load images binarize
    graph = phm_seg.graph_from_voxel_grid(voxel_grid)

    voxel_skeleton = phm_seg.skeletonize(voxel_grid, graph)

    image_projection = list()
    for angle in [0, 120, 270]:
        projection = calibration.get_projection("side", angle)
        image_projection.append((bin_images["side"][angle], projection))

    voxel_skeleton = phm_seg.segment_reduction(
        voxel_skeleton, image_projection, required_visible=1, nb_min_pixel=100
    )


def test_project_voxels_on_pixels_covers_same_pixels_as_image():
    calibration = phm_data.load_calibration(data_dir)
    bin_images = phm_data.bin_images(data_dir)
    voxel_grid = phm_data.voxel_grid(data_dir, 32)
    voxels_position = numpy.array(list(voxel_grid.voxels_position))

    for angle in [0, 120, 270]:
        projection = calibration.get_projection("side", angle)
        shape = bin_images["side"][angle].shape
        # the smaller shape crops the projection: some voxels are out of the image
        for image_shape in [shape, (shape[0] // 2, shape[1] // 2)]:
            image = project_voxel_centers_on_image(
                voxels_position, voxel_grid.voxels_size, image_shape, projection
            )
            pixels = _project_voxels_on_pixels(
                voxels_position, voxel_grid.voxels_size, image_shape, projection
            )
            assert numpy.array_equal(pixels, numpy.flatnonzero(image))


def test_project_voxels_on_pixels_out_of_image():
    pixels = _project_voxels_on_pixels(
        numpy.array([[0.0, 0.0, 0.0]]),
        1,
        (10, 10),
        lambda corners: corners[:, :2] + 100,
    )
    assert len(pixels) == 0


class _Segment:
    def __init__(self, position, length=1):
        self.voxels_position = [position]
        self.polyline = [position] * length


def _project_on_x_y(corners):
    return corners[:, :2]


def test_segment_reduction_removes_covered_segments():
    image = numpy.ones((20, 20), dtype=numpy.uint8)
    inside = _Segment((5.5, 5.5, 0.0), length=1)
    covering = _Segment((5.5, 5.5, 0.0), length=2)
    separate = _Segment((15.5, 15.5, 0.0), length=3)
    skeleton = VoxelSkeleton([separate, inside, covering], 3)

    reduced = phm_seg.segment_reduction(
        skeleton, [(image, _project_on_x_y)], required_visible=1, nb_min_pixel=1
    )

    # the shortest of two identical segments is removed, then the other one is kept
    assert reduced.segments == [covering, separate]


def test_segment_reduction_ignores_pixels_of_the_background():
    image = numpy.zeros((20, 20), dtype=numpy.uint8)
    skeleton = VoxelSkeleton([_Segment((5.5, 5.5, 0.0))], 3)

    reduced = phm_seg.segment_reduction(
        skeleton, [(image, _project_on_x_y)], required_visible=1, nb_min_pixel=1
    )

    assert reduced.segments == []


def test_segment_reduction_counts_images_where_segment_is_visible():
    visible = numpy.ones((20, 20), dtype=numpy.uint8)
    hidden = numpy.zeros((20, 20), dtype=numpy.uint8)
    skeleton = VoxelSkeleton([_Segment((5.5, 5.5, 0.0))], 3)
    image_projection = [(visible, _project_on_x_y), (hidden, _project_on_x_y)]

    for required_visible, nb_segments in [(1, 1), (2, 0)]:
        reduced = phm_seg.segment_reduction(
            skeleton, image_projection, required_visible, nb_min_pixel=1
        )
        assert len(reduced.segments) == nb_segments
