# -*- python -*-
#
#       test_multi_view_reconstruction_model.py :
#
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
#       ========================================================================

#       ========================================================================
#       External Import
import numpy

#       ========================================================================
#       Local Import
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation

#       ========================================================================
#       Code


def test_multi_view_reconstruction_model_1():

    size = 10
    radius = 8
    point_3d = (-472, -472, 200)

    points = alinea.phenomenal.data_creation.build_object_1(
        size, radius, point_3d)

    # alinea.phenomenal.result_viewer.show_points_3d(points)

    calibration = alinea.phenomenal.calibration_model.\
        Calibration.read_calibration('tests/test_calibration_model')

    images = alinea.phenomenal.data_creation.build_image_from_points_3d(
        points, radius, calibration, step=30)

    # alinea.phenomenal.result_viewer.show_image(images[0])

    points = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images, calibration, precision=8, verbose=True)

    mat, _, _ = alinea.phenomenal.data_transformation.points_3d_to_matrix(
        points, radius)

    # alinea.phenomenal.result_viewer.show_points_3d(points)

    assert mat.size == 1728
    assert (mat == 1).all()


def test_multi_view_reconstruction_model_2():

    radius = 4
    images = alinea.phenomenal.data_creation.build_images_1()

    calibration = alinea.phenomenal.calibration_model.\
        Calibration.read_calibration('tests/test_calibration_model')

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images, calibration, precision=radius, verbose=True)

    assert len(points_3d) == 7432

    for angle in images:
        image = alinea.phenomenal.multi_view_reconstruction.\
            project_points_on_image(points_3d,
                                    radius,
                                    images[angle],
                                    calibration,
                                    angle)

        img = numpy.subtract(image, images[0])
        img[img == -255] = 255

        # alinea.phenomenal.result_viewer.show_images([images[angle], img, image])
        print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img)
        assert numpy.count_nonzero(img) < 4000


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_multi_view_reconstruction_model_1()
    test_multi_view_reconstruction_model_2()
