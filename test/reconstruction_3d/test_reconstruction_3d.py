# -*- python -*-
#
#       test_octree: Module Description
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
import cv2
import glob

#       =======================================================================
#       Local Import 

import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import tools_test

#       =======================================================================


def test_reconstruction_3d():

    #   =======================================================================

    my_calibration = calibration_chessboard.Calibration.read_calibration(
        '../calibration/calibration')


    directory = '../../local/data/tests/Samples_binarization_2/'
    # directory = '../../local/data/tests/Samples_binarization_4/'
    # directory = '../../local/data/tests/Samples_binarization_5/'
    # directory = '../../local/data/tests/Samples_binarization_2/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
        if angles[i] < 120:
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)


    octree_result = reconstruction_3d.reconstruction_3d(
        images, my_calibration, 10)

    tools_test.show_cube(octree_result, 9, "OpenCv")

    reconstruction_3d.reprojection_3d_objects_to_images(
        images, octree_result, my_calibration)



if __name__ == "__main__":
    test_reconstruction_3d()