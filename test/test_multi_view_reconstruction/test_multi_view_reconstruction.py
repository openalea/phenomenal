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
    split_voxel_centers_in_eight,
    reconstruction_3d)

# ==============================================================================


def test_split_voxel_centers_in_eight_1():

    voxels_size = 16
    voxels_position = numpy.array([[0.0, 0.0, 0.0]])

    res = split_voxel_centers_in_eight(voxels_position, voxels_size)

    ref = numpy.array([[-4., -4., -4.],
                       [4., -4., -4.],
                       [-4., 4., -4.],
                       [-4., -4., 4.],
                       [4., 4., -4.],
                       [4., -4., 4.],
                       [-4., 4., 4.],
                       [4., 4., 4.]])

    assert numpy.array_equal(ref, res)


def test_split_voxel_centers_in_eight_2():

    voxels_size = 16
    voxels_position = numpy.array([])

    res = split_voxel_centers_in_eight(voxels_position, voxels_size)

    assert numpy.array_equal(res, numpy.array([]))


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

        ref = False
        if with_ref:
            if angle == 0:
                img[:] = 0
            if angle == 90:
                ref = True

        iv = ImageView(img, projection, inclusive=False, ref=ref)
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
                           voxels_size=voxels_size,
                           verbose=False)

    assert len(vg.voxels_position) > 0


def test_reconstruction_3d_2():

    image_views = get_image_views_cube_projected()

    vg = reconstruction_3d(image_views,
                            voxels_size=20,
                            verbose=False)

    assert len(vg.voxels_position) > 0

    false_positive, true_negative = reconstruction_error(vg, image_views)


def test_reconstruction_3d_3():

    image_views = get_image_views_cube_projected(with_ref=True)

    vg = reconstruction_3d(image_views,
                           voxels_size=40,
                           verbose=True,
                           error_tolerance=0)

    assert len(vg.voxels_position) > 0


# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
