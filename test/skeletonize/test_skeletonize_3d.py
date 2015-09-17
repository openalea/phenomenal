# -*- python -*-
#
#       test_skeletonize_3d.py :
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
import glob
import cv2
from mayavi import mlab


#       ========================================================================
#       Local Import
import alinea.phenomenal.skeletonize_3d as skeletonize_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import phenomenal.test.tools_test as tools_test
#       ========================================================================
#       Code


def test_skeletonize_3d():
    #   ========================================================================
    #   LOAD IMAGE & ANGLE
    #   Samples_binarization_2 : Tree
    #   Samples_binarization_3 - 5 : etc...

    directory = '..\\..\\local\\data\\tests\\Samples_binarization_7\\'

    files = glob.glob(directory + '*.png')

    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    image_0_240 = dict()
    for angle in images:
        if angle <= 240:
            image_0_240[angle] = images[angle]

    cubes = reconstruction_3d.reconstruction_3d(
        image_0_240, opencv_calibration, 5)

    #   ========================================================================

    cubes = reconstruction_3d.change_orientation(cubes)

    #   ========================================================================

    mlab.figure("3D Reconstruction")
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()
    mlab.clf()
    mlab.close()

    #   ========================================================================

    # skeletonize.skeletonize_3d_transform_distance(opencv_cubes)

    # skeletonize_3d.test_skeletonize_3d(cubes, 10, 20)

    skeleton_3d = skeletonize_3d.skeletonize_3d_segment(cubes, 10, 50)

    #   ========================================================================

    mlab.figure("Skeleton")
    tools_test.plot_vectors(skeleton_3d)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_skeletonize_3d()
