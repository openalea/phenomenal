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


import numpy
import pytest

import openalea.phenomenal.data as phm_data
import openalea.phenomenal.object as phm_obj
import openalea.phenomenal.multi_view_reconstruction as phm_mvr

from pathlib import Path
test_subdir = Path(__file__).parent.parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir / "data" / "plant_1"

# ==============================================================================


def test_split_voxel_centers_in_eight_1():
    voxels = phm_mvr.Voxels(numpy.array([[0.0, 0.0, 0.0]]), 16)
    result_voxels = phm_mvr.split_voxels_in_eight(voxels)

    ref_position = numpy.array(
        [
            [-4.0, -4.0, -4.0],
            [4.0, -4.0, -4.0],
            [-4.0, 4.0, -4.0],
            [-4.0, -4.0, 4.0],
            [4.0, 4.0, -4.0],
            [4.0, -4.0, 4.0],
            [-4.0, 4.0, 4.0],
            [4.0, 4.0, 4.0],
        ]
    )

    assert numpy.array_equal(ref_position, result_voxels.position)


def test_split_voxel_centers_in_eight_2():
    voxels = phm_mvr.Voxels(numpy.array([]), 16)
    res = phm_mvr.split_voxels_in_eight(voxels)
    assert numpy.array_equal(res.position, numpy.array([]))


# ==============================================================================


def test_get_voxels_corners():
    voxels_position = numpy.array([[0.0, 0.0, 0.0], [4.0, 4.0, 4.0]])
    voxels_size = 16

    res = phm_mvr.get_voxels_corners(voxels_position, voxels_size / 2)
    ref = numpy.array(
        [
            [
                [-4.0, -4.0, -4.0],
                [4.0, -4.0, -4.0],
                [-4.0, 4.0, -4.0],
                [-4.0, -4.0, 4.0],
                [4.0, 4.0, -4.0],
                [4.0, -4.0, 4.0],
                [-4.0, 4.0, 4.0],
                [4.0, 4.0, 4.0]
            ],
            [
                [0.0, 0.0, 0.0],
                [8.0, 0.0, 0.0],
                [0.0, 8.0, 0.0],
                [0.0, 0.0, 8.0],
                [8.0, 8.0, 0.0],
                [8.0, 0.0, 8.0],
                [0.0, 8.0, 8.0],
                [8.0, 8.0, 8.0]
            ],
        ]
    )

    assert numpy.array_equal(ref, res)


# ==============================================================================


def test_get_bounding_box_voxel_projected_1():
    voxels_position = numpy.array([[0, 0, 0]])
    voxel_size = 20

    def projection(pt):
        return numpy.column_stack((pt[:, 0], pt[:, 1], pt[:, 2]))

    vp = phm_mvr.project_voxels(voxels_position, voxel_size, projection)
    res = phm_mvr.get_bounding_box_voxel_projected(vp)

    ref = numpy.array([[-10, -10, 10, 10]])

    assert numpy.allclose(ref, res)


def test_get_bounding_box_voxel_projected_2():
    angle = 0
    calibration = phm_data.load_calibration(data_dir)
    projection = calibration.get_projection("side", angle, depth=True)

    voxels_position = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    voxels_size = 8

    vp = phm_mvr.project_voxels(voxels_position, voxels_size, projection)
    res = phm_mvr.get_bounding_box_voxel_projected(vp)

    ref = numpy.array(
        [
            [1017.309, 1258.280, 1025.788, 1265.171],
            [1017.309, 1258.280, 1025.788, 1265.171],
            [1017.309, 1258.280, 1025.788, 1265.171],
        ]
    )

    assert numpy.allclose(ref, res)


def test_split_and_projection():
    angle = 0
    calibration = phm_data.load_calibration(data_dir)
    projection = calibration.get_projection("side", angle, depth=True)

    voxels_position = numpy.array([[0, 0, 0]])
    voxels_size = 64

    for i in range(5):
        vp = phm_mvr.project_voxels(voxels_position, voxels_size, projection)
        res = phm_mvr.get_bounding_box_voxel_projected(vp)
        res = numpy.floor(res).astype(int)

        img = numpy.zeros((3000, 3000))
        for x_min, y_min, x_max, y_max in res:
            img[y_min : y_max + 1, x_min : x_max + 1] = 255

        assert 3864 == numpy.count_nonzero(img)

        img = phm_mvr.project_voxel_centers_on_image(
            voxels_position, voxels_size, (3000, 3000), projection
        )
        assert 3864 == numpy.count_nonzero(img)

        voxels = phm_mvr.split_voxels_in_eight(
            phm_mvr.Voxels(voxels_position, voxels_size)
        )
        voxels_position = voxels.position
        voxels_size = voxels.size


# ==============================================================================


def get_image_views_cube_projected():
    # ==========================================================================
    # Create object
    voxels_size = 10
    voxels_position = phm_data.build_cube(
        cube_size=10, voxels_size=voxels_size, voxels_position=(0, 0, 0)
    )

    assert len(voxels_position) == 1000
    volume = len(voxels_position) * (10**3)
    assert volume == 1000000

    # ==========================================================================
    calibration = phm_data.load_calibration(data_dir)

    shape_image = (2454, 2056)
    image_views = dict()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection("side", angle, depth=True)

        img = phm_mvr.project_voxel_centers_on_image(
            voxels_position, voxels_size, shape_image, projection
        )
        iv = phm_obj.ImageView(img, projection)
        image_views[f'side_{angle}'] = iv

    return image_views


def test_reconstruction_3d_plant1():
    # Load images binarize
    bin_images = phm_data.bin_images(data_dir)
    calibration = phm_data.load_calibration(data_dir)

    image_views = phm_obj.as_image_views(phm_obj.iter_images(bin_images), calibration)
    vg = phm_mvr.reconstruction_3d(
        image_views, voxels_size=64, error_tolerance=0)
    assert len(vg.voxels_position) > 0
    vg = phm_mvr.reconstruction_3d(
        image_views, voxels_size=64, error_tolerance=-1)
    assert len(vg.voxels_position) > 0


def test_reconstruction_3d_cube():
    voxels_size = 20
    error_tolerance = 0

    image_views = get_image_views_cube_projected()

    vg = phm_mvr.reconstruction_3d(
        image_views, voxels_size=voxels_size, error_tolerance=error_tolerance
    )

    assert len(vg.voxels_position) > 0
    false_positive, true_negative = phm_mvr.reconstruction_error(vg, image_views)


def test_reconstruction_3d_neighbours():
    voxels_size = 40
    error_tolerance = 0

    image_views = get_image_views_cube_projected()
    image_views['side_0'].image[:] = 0
    vg = phm_mvr.reconstruction_3d_neighbours(
        image_views, voxels_size=voxels_size, error_tolerance=error_tolerance, reference_views=['side_90']
    )

    assert len(vg.voxels_position) > 0


def _projection_in_front(pts):
    """Project x, y, z on u, v with every point in front of the camera"""
    return numpy.asarray(pts, dtype=float).reshape(-1, 3) + [0, 0, 100.0]


def _foreground_on_all_borders():
    image = numpy.zeros((100, 100), dtype=numpy.uint8)
    image[0, :] = image[-1, :] = image[:, 0] = image[:, -1] = 255
    return image


def _is_visible(position, image, inclusive):
    return phm_mvr.voxels_is_visible_in_image(
        numpy.array([position], dtype=float),
        10,
        image,
        phm_mvr.integral_image(image),
        _projection_in_front,
        inclusive=inclusive,
    )[0]


OUTSIDE_IMAGE = [(200, 50, 0), (50, 200, 0), (-200, 50, 0), (50, -200, 0)]


@pytest.mark.parametrize("position", OUTSIDE_IMAGE)
def test_voxel_outside_image_is_kept_if_inclusive(position):
    assert _is_visible(position, _foreground_on_all_borders(), inclusive=True)


@pytest.mark.parametrize("position", OUTSIDE_IMAGE)
def test_voxel_outside_image_is_rejected_if_not_inclusive(position):
    assert not _is_visible(position, _foreground_on_all_borders(), inclusive=False)


def test_voxel_partly_outside_image_uses_its_visible_pixels_if_not_inclusive():
    image = numpy.zeros((100, 100), dtype=numpy.uint8)
    assert not _is_visible((99, 50, 0), image, inclusive=False)
    # away from the center pixel of the voxel, which has its own fast check
    image[47, 96] = 255
    assert _is_visible((99, 50, 0), image, inclusive=False)


@pytest.mark.parametrize("position", OUTSIDE_IMAGE)
def test_project_voxel_outside_image_paints_nothing(position):
    image = phm_mvr.project_voxel_centers_on_image(
        numpy.array([position], dtype=float), 10, (100, 100), _projection_in_front
    )
    assert not image.any()


def test_project_voxel_partly_outside_image_paints_its_visible_pixels():
    image = phm_mvr.project_voxel_centers_on_image(
        numpy.array([(99, 50, 0)], dtype=float),
        10,
        (100, 100),
        _projection_in_front,
        value=1,
    )
    rows, columns = numpy.nonzero(image)
    assert (columns.min(), columns.max()) == (94, 99)
    assert (rows.min(), rows.max()) == (45, 55)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
