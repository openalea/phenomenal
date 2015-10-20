# -*- python -*-
#
#       test_multi_view_reconstruction_manual.py :
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
import alinea.phenomenal.calibration_manual
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation

#       ========================================================================
#       Code


def test_multi_view_reconstruction_manual_1():
    size = 10
    radius = 1
    point_3d = (68, 68, 100)

    points = alinea.phenomenal.data_creation.build_object_1(
        size, radius, point_3d)

    calibration = alinea.phenomenal.calibration_manual.Calibration()

    images = alinea.phenomenal.data_creation.build_image_from_points_3d(
        points, radius, calibration, step=30)

    points = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images, calibration, precision=radius, verbose=True)

    mat, _ = alinea.phenomenal.data_transformation.points_3d_to_matrix(
        points, radius)

    assert mat.size == 1331
    print numpy.shape(mat)


def test_multi_view_reconstruction_manual_2():
    radius = 0.5

    images = alinea.phenomenal.data_creation.build_images_1()

    calibration = alinea.phenomenal.calibration_manual.Calibration()

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images, calibration, precision=radius, verbose=True)

    print len(points_3d)

    for angle in images:
        image = alinea.phenomenal.multi_view_reconstruction.\
            project_points_on_image(points_3d,
                                    radius,
                                    images[angle],
                                    calibration,
                                    angle)

        img = numpy.subtract(image, images[0])
        img[img == -255] = 255
        print numpy.count_nonzero(img)
        assert numpy.count_nonzero(img) < 6000


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_multi_view_reconstruction_manual_1()
    test_multi_view_reconstruction_manual_2()
