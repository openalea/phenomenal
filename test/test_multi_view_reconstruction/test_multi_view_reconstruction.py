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
            [-4.0, -4.0, -4.0],
            [4.0, -4.0, -4.0],
            [-4.0, 4.0, -4.0],
            [-4.0, -4.0, 4.0],
            [4.0, 4.0, -4.0],
            [4.0, -4.0, 4.0],
            [-4.0, 4.0, 4.0],
            [4.0, 4.0, 4.0],
            [0.0, 0.0, 0.0],
            [8.0, 0.0, 0.0],
            [0.0, 8.0, 0.0],
            [0.0, 0.0, 8.0],
            [8.0, 8.0, 0.0],
            [8.0, 0.0, 8.0],
            [0.0, 8.0, 8.0],
            [8.0, 8.0, 8.0],
        ]
    )

    assert numpy.array_equal(ref, res)


# ==============================================================================


def test_get_bounding_box_voxel_projected_1():
    voxels_position = numpy.array([[0, 0, 0]])
    voxel_size = 20

    def projection(pt):
        return numpy.column_stack((pt[:, 0], pt[:, 1]))

    res = phm_mvr.get_bounding_box_voxel_projected(
        voxels_position, voxel_size, projection
    )
    ref = numpy.array([[-10, -10, 10, 10]])

    assert numpy.allclose(ref, res)


def test_get_bounding_box_voxel_projected_2():
    angle = 0
    calibration = phm_data.load_calibration(data_dir)
    projection = calibration.get_projection("side", angle)

    voxels_position = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    voxels_size = 8

    res = phm_mvr.get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection
    )

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
    projection = calibration.get_projection("side", angle)

    voxels_position = numpy.array([[0, 0, 0]])
    voxels_size = 64

    for i in range(5):
        res = phm_mvr.get_bounding_box_voxel_projected(
            voxels_position, voxels_size, projection
        )
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
        projection = calibration.get_projection("side", angle)

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


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith("test_"):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
