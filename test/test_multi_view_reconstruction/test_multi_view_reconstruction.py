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
import numpy
import time

from openalea.phenomenal.data.data_creation import (
    build_cube)

from openalea.phenomenal.data.plant_1 import (
    plant_1_calibration_camera_side,
    plant_1_images_binarize)

from openalea.phenomenal.object import (
    ImageView)

from openalea.phenomenal.multi_view_reconstruction import (
    get_voxels_corners,
    get_bounding_box_voxel_projected,
    project_voxel_centers_on_image,
    reconstruction_error,
    split_voxels_in_eight,
    reconstruction_3d,
    Voxels)

# ==============================================================================


def test_split_voxel_centers_in_eight_1():

    voxels = Voxels(numpy.array([[0.0, 0.0, 0.0]]), 16)
    result_voxels = split_voxels_in_eight(voxels)

    ref_position = numpy.array([[-4., -4., -4.],
                                [4., -4., -4.],
                                [-4., 4., -4.],
                                [-4., -4., 4.],
                                [4., 4., -4.],
                                [4., -4., 4.],
                                [-4., 4., 4.],
                                [4., 4., 4.]])

    assert numpy.array_equal(ref_position, result_voxels.position)


def test_split_voxel_centers_in_eight_2():
    voxels = Voxels(numpy.array([]), 16)
    res = split_voxels_in_eight(voxels)
    assert numpy.array_equal(res.position, numpy.array([]))


# ==============================================================================


def test_get_voxels_corners():

    voxels_position = numpy.array([[0.0, 0.0, 0.0],
                                   [4.0, 4.0, 4.0]])
    voxels_size = 16

    res = get_voxels_corners(voxels_position, voxels_size / 2)
    ref = numpy.array([[-4., - 4., - 4.],
                       [4., -4., -4.],
                       [-4., 4., -4.],
                       [-4., -4., 4.],
                       [4., 4., -4.],
                       [4., -4., 4.],
                       [-4., 4., 4.],
                       [4., 4., 4.],
                       [0., 0., 0.],
                       [8., 0., 0.],
                       [0., 8., 0.],
                       [0., 0., 8.],
                       [8., 8., 0.],
                       [8., 0., 8.],
                       [0., 8., 8.],
                       [8., 8., 8.]])

    assert numpy.array_equal(ref, res)

# ==============================================================================


def test_get_bounding_box_voxel_projected_1():

    voxel_center = numpy.array([[0, 0, 0]])
    voxel_size = 20

    projection = lambda pt: numpy.column_stack((pt[:, 0], pt[:, 1]))

    res = get_bounding_box_voxel_projected(voxel_center, voxel_size, projection)
    ref = numpy.array([[-10, -10, 10, 10]])

    assert numpy.allclose(ref, res)


def test_get_bounding_box_voxel_projected_2():

    angle = 0
    calibration = plant_1_calibration_camera_side()
    projection = calibration.get_projection(angle)

    voxels_position = numpy.array([[0, 0, 0],
                                   [0, 0, 0],
                                   [0, 0, 0]])
    voxels_size = 8

    res = get_bounding_box_voxel_projected(voxels_position,
                                           voxels_size,
                                           projection)

    ref = numpy.array([[1017.309, 1258.280, 1025.788, 1265.171],
                       [1017.309, 1258.280, 1025.788, 1265.171],
                       [1017.309, 1258.280, 1025.788, 1265.171]])

    assert numpy.allclose(ref, res)


def test_split_and_projection():

    angle = 0
    calibration = plant_1_calibration_camera_side()
    projection = calibration.get_projection(angle)

    voxels_position = numpy.array([[0, 0, 0]])
    voxels_size = 64

    for i in range(5):
        res = get_bounding_box_voxel_projected(voxels_position,
                                               voxels_size,
                                               projection)
        res = numpy.floor(res).astype(int)

        img = numpy.zeros((3000, 3000))
        for x_min, y_min, x_max, y_max in res:
            img[y_min:y_max + 1, x_min:x_max + 1] = 255

        assert 3864 == numpy.count_nonzero(img)

        img = project_voxel_centers_on_image(voxels_position, voxels_size,
                                             (3000, 3000), projection)
        assert 3864 == numpy.count_nonzero(img)

        voxels = split_voxels_in_eight(Voxels(voxels_position, voxels_size))
        voxels_position = voxels.position
        voxels_size = voxels.size


def test_split_and_projection():
    angle = 0
    calibration = plant_1_calibration_camera_side()
    projection = calibration.get_projection(angle)

    voxels_position = numpy.array([[0, 0, 0]])
    voxels_size = 64

    for i in range(5):
        res = get_bounding_box_voxel_projected(voxels_position,
                                               voxels_size,
                                               projection)
        res = numpy.floor(res).astype(int)

        img = numpy.zeros((3000, 3000))
        for x_min, y_min, x_max, y_max in res:
            img[y_min:y_max + 1, x_min:x_max + 1] = 255

        assert 3864 == numpy.count_nonzero(img)

        img = project_voxel_centers_on_image(voxels_position, voxels_size,
                                             (3000, 3000), projection)
        assert 3864 == numpy.count_nonzero(img)

        voxels = split_voxels_in_eight(Voxels(voxels_position, voxels_size))
        voxels_position = voxels.position
        voxels_size = voxels.size

# ==============================================================================


def get_image_views_cube_projected(with_ref=False):

    # ==========================================================================
    # Create object
    voxels_size = 10
    voxels_position = build_cube(cube_size=10,
                                 voxels_size=voxels_size,
                                 voxels_position=(0, 0, 0))

    assert len(voxels_position) == 1000
    volume = len(voxels_position) * (10**3)
    assert volume == 1000000

    # ==========================================================================
    calibration = plant_1_calibration_camera_side()

    shape_image = (2454, 2056)
    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)

        img = project_voxel_centers_on_image(voxels_position,
                                             voxels_size,
                                             shape_image,
                                             projection)

        image_ref = None
        if with_ref:
            if angle == 0:
                img[:] = 0
            if angle == 90:
                image_ref = img

        iv = ImageView(img, projection, inclusive=False, image_ref=image_ref)
        image_views.append(iv)

    return image_views


def test_reconstruction_3d_1():

    # Load images binarize
    images = plant_1_images_binarize()
    calibration = plant_1_calibration_camera_side()

    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)
        iv = ImageView(images[angle], projection, inclusive=False)
        image_views.append(iv)

    voxels_size = 64
    # Multi-view reconstruction
    vg = reconstruction_3d(image_views,
                           voxels_size=voxels_size)

    assert len(vg.voxels_position) > 0


def test_reconstruction_3d_2():

    image_views = get_image_views_cube_projected()

    vg = reconstruction_3d(image_views,
                           voxels_size=20)

    assert len(vg.voxels_position) > 0

    false_positive, true_negative = reconstruction_error(vg, image_views)


def test_reconstruction_3d_3():

    image_views = get_image_views_cube_projected(with_ref=True)

    vg = reconstruction_3d(image_views,
                           voxels_size=40,
                           error_tolerance=0)

    assert len(vg.voxels_position) > 0


# ==============================================================================

if __name__ == "__main__":

    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
