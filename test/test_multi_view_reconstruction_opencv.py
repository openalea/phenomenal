# -*- python -*-

#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import numpy

import alinea.phenomenal.calibration_opencv
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation

from alinea.phenomenal.calibration_opencv import (CameraParameters,
                                                  Projection)
from alinea.phenomenal.viewer import show_points_3d
from alinea.phenomenal.plant_1 import (plant_1_images_binarize,
                                       plant_1_params_camera_opencv_path)
# ==============================================================================


def test_multi_view_reconstruction_opencv_1():
    size = 10
    radius = 8
    point_3d = (-472, -472, 200)

    points = alinea.phenomenal.data_creation.build_object_1(
        size, radius, point_3d)

    cp = CameraParameters.read(plant_1_params_camera_opencv_path())
    p = Projection(cp)

    images = alinea.phenomenal.data_creation.build_image_from_points_3d(
        points, radius, p, stop=120, step=30)

    images_selected = dict()
    for angle in [0, 30, 60, 90]:
        images_selected[angle] = images[angle]

    points = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images_selected, p, radius, verbose=True)

    mat, _, _ = alinea.phenomenal.data_transformation.points_3d_to_matrix(
        points, radius)

    print mat.size
    assert mat.size == 5236
    print numpy.shape(mat)


def test_multi_view_reconstruction_opencv_2():
    radius = 4
    images = alinea.phenomenal.data_creation.build_images_1()

    cp = CameraParameters.read(plant_1_params_camera_opencv_path())
    p = Projection(cp)

    images_selected = dict()
    for angle in [0, 30, 60, 90]:
        images_selected[angle] = images[angle]

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images_selected, p, radius, verbose=True)

    for angle in [0, 30, 60, 90]:
        image = alinea.phenomenal.multi_view_reconstruction.\
            project_points_on_image(points_3d,
                                    radius,
                                    images_selected[angle].shape,
                                    p,
                                    angle)

        img = numpy.subtract(image, images_selected[0])
        img[img == -255] = 255
        print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img)
        assert numpy.count_nonzero(img) < 9000


def test_multi_view_reconstruction_opencv_3():
    radius = 10

    cp = CameraParameters.read(plant_1_params_camera_opencv_path())
    p = Projection(cp)

    images_binarize = plant_1_images_binarize()
    images_selected = dict()
    for angle in [0, 30, 60, 90]:
        images_selected[angle] = images_binarize[angle]

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images_selected, p, radius, verbose=True)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_multi_view_reconstruction_opencv_1()
    test_multi_view_reconstruction_opencv_2()
    test_multi_view_reconstruction_opencv_3()
