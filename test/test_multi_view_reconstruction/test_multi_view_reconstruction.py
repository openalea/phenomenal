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
        _projection_in_front,
        inclusive=inclusive,
        image_int=phm_mvr.integral_image(image),
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


def _projection_without_depth(pts):
    return numpy.asarray(pts, dtype=float).reshape(-1, 3)[:, :2]


@pytest.mark.parametrize("nb_voxels", [1, 2, 3, 6])
def test_project_voxels_rejects_projection_without_depth(nb_voxels):
    # 3 voxels are the case that could silently be reshaped to the expected shape
    positions = numpy.zeros((nb_voxels, 3))
    with pytest.raises(ValueError, match="depth"):
        phm_mvr.project_voxels(positions, 10, _projection_without_depth)


def test_voxels_is_visible_rejects_projection_without_depth():
    image = numpy.zeros((100, 100), dtype=numpy.uint8)
    with pytest.raises(ValueError, match="depth"):
        phm_mvr.voxels_is_visible_in_image(
            numpy.zeros((1, 3)), 10, image, _projection_without_depth
        )


def test_voxels_is_visible_positional_call_and_default_integral():
    image = numpy.zeros((100, 100), dtype=numpy.uint8)
    # away from the center pixel of the voxel, which has its own fast check
    image[47, 53] = 255
    position = numpy.array([(50, 50, 0)], dtype=float)
    assert phm_mvr.voxels_is_visible_in_image(
        position, 10, image, _projection_in_front, False
    )[0]
    assert phm_mvr.voxels_is_visible_in_image(
        position, 10, image, _projection_in_front, False,
        image_int=phm_mvr.integral_image(image),
    )[0]


def _project_positions(positions):
    return phm_mvr.project_voxels_position_on_image(
        numpy.array(positions, dtype=float), 10, (100, 100), _projection_in_front
    )


def test_project_voxels_position_paints_voxel():
    rows, columns = numpy.nonzero(_project_positions([(50, 50, 0)]))
    assert (columns.min(), columns.max()) == (45, 55)
    assert (rows.min(), rows.max()) == (45, 55)


def test_project_voxels_position_skips_voxel_behind_camera():
    image = _project_positions([(20, 20, 0), (70, 70, -200)])
    assert image[20, 20] > 0
    assert image[70, 70] == 0


@pytest.mark.parametrize("position", OUTSIDE_IMAGE)
def test_project_voxels_position_outside_image_paints_nothing(position):
    assert not _project_positions([position]).any()


def test_project_voxels_position_visible_on_a_single_row():
    # all corners are clipped onto the same line: not a valid 2D hull
    rows, _ = numpy.nonzero(_project_positions([(50, -5, 0)]))
    assert rows.min() == rows.max() == 0


@pytest.mark.parametrize(
    "reconstruction",
    [phm_mvr.tolerant_reconstruction, phm_mvr.multi_tolerant_reconstruction],
)
def test_tolerant_reconstructions_default_clear_outside(reconstruction):
    image = numpy.full((100, 100), 255, dtype=numpy.uint8)
    views = {"view": phm_obj.ImageView(image, _projection_in_front)}
    assert reconstruction(views, voxels_size=256) is not None


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
