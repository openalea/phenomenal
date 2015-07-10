# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import

#       =======================================================================
#       Local Import 
import tools_test
import alinea.phenomenal.calibration_manual as calibration_manual
import alinea.phenomenal.reconstruction_3d as reconstruction_3d


#       =======================================================================
#       Code


def test_reconstruction_3d_samples_binarization_1():
    #   =======================================================================
    #   Input
    images_path = ['../../share/data/Samples_binarization_1/top.png',
                   '../../share/data/Samples_binarization_1/side0.png',
                   '../../share/data/Samples_binarization_1/side90.png']

    angles = [-1, 0, 90]

    images = tools_test.load_images(images_path)

    #   =======================================================================
    #   Binarize images
    for im in images:
        im[im == 255] = 0
        im[im != 0] = 255

    # =======================================================================
    #   Load manual configuration

    camera_configuration = calibration_manual.CameraConfiguration()
    calibration = calibration_manual.Calibration(camera_configuration)

    #   =======================================================================
    #   Reconstruction 3D

    octree_result = reconstruction_3d.reconstruction_3d_manual_calibration(
        images, angles, calibration, 1)

    tools_test.show_cube(octree_result, 1.0)


def test_reconstruction_3d_samples_binarization_2():
    #   =======================================================================
    #   Input

    images_path = ['../../share/data/Samples_binarization_2/top.png',
                   '../../share/data/Samples_binarization_2/0.png',
                   '../../share/data/Samples_binarization_2/30.png',
                   '../../share/data/Samples_binarization_2/60.png',
                   '../../share/data/Samples_binarization_2/90.png',
                   '../../share/data/Samples_binarization_2/120.png',
                   '../../share/data/Samples_binarization_2/150.png',
                   '../../share/data/Samples_binarization_2/180.png',
                   '../../share/data/Samples_binarization_2/210.png',
                   '../../share/data/Samples_binarization_2/240.png',
                   '../../share/data/Samples_binarization_2/270.png',
                   '../../share/data/Samples_binarization_2/300.png',
                   '../../share/data/Samples_binarization_2/330.png']

    angles = [-1, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]

    images = tools_test.load_images(images_path)

    camera_configuration = calibration_manual.CameraConfiguration()
    calibration = calibration_manual.Calibration(camera_configuration)

    #   =======================================================================
    #   Reconstruction 3D

    octree_result = reconstruction_3d.reconstruction_3d_manual_calibration(
        images, angles, calibration, 1)

    tools_test.show_cube(octree_result, 1)


test_reconstruction_3d_samples_binarization_1()
test_reconstruction_3d_samples_binarization_2()
