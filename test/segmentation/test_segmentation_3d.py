# -*- python -*-
#
#       test_segmentation_3d.py.py : 
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
import numpy as np
import cv2
from mayavi import mlab


#       ========================================================================
#       Local Import
import alinea.phenomenal.skeletonize_3d as skeletonize_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.segmentation_3d as segmentation_3d
import phenomenal.test.tools_test as tools_test
#       ========================================================================
#       Code

def test_segmentation_3d():
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

    cubes = reconstruction_3d.change_orientation(cubes)

    skeleton_3d = skeletonize_3d.skeletonize_3d_segment(cubes, 10, 50)
#   ========================================================================

    mlab.figure("Skeleton")
    tools_test.plot_vectors(skeleton_3d)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    stem, leaves, segments = \
        segmentation_3d.segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mlab.figure("Organs")
    for leaf in leaves:
        tools_test.plot_segments(leaf.segments)
    tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    mlab.figure("Propagation")

    stem_cubes = give_cube(stem, cubes[0].radius)
    color = tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(stem_cubes, color=color, scale_factor=3)

    for leaf in leaves:
        leaf_cubes = give_cube(leaf, cubes[0].radius)
        color = tools_test.plot_segments(leaf.segments)
        tools_test.plot_cubes(leaf_cubes, color=color, scale_factor=3)

    # tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    from random import uniform
    #
    stem_cubes = reconstruction_3d.change_orientation(stem_cubes)
    #
    for angle in image_0_240:

        image = image_0_240[angle]

        for leaf in leaves:
            color = (int(uniform(0, 255)),
                     int(uniform(0, 255)),
                     int(uniform(0, 255)))

            leaf_cube = give_cube(leaf, cubes[0].radius)
            leaf_cube = reconstruction_3d.change_orientation(leaf_cube)

            image = reconstruction_3d.re_projection_cubes_to_image(
                leaf_cube,
                image,
                opencv_calibration[angle],
                color=color)

        color = (int(uniform(0, 255)),
                 int(uniform(0, 255)),
                 int(uniform(0, 255)))

        image = reconstruction_3d.re_projection_cubes_to_image(
            stem_cubes,
            image,
            opencv_calibration[angle],
            color=color)

        tools_test.show_image(image, str(angle))

    #   ========================================================================

    for angle in image_0_240:

        image = image_0_240[angle]

        for leaf in leaves:
            leaf_cube = give_cube(leaf, cubes[0].radius)
            leaf_cube = reconstruction_3d.change_orientation(leaf_cube)

            image = reconstruction_3d.re_projection_cubes_to_image(
                leaf_cube,
                image,
                opencv_calibration[angle],
                color=(0, 0, 0))

        image = reconstruction_3d.re_projection_cubes_to_image(
            stem_cubes,
            image,
            opencv_calibration[angle],
            color=(255, 255, 255))

        # tools_test.show_image(image, str(angle))

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image[image == 255] = 1

        import alinea.phenomenal.skeletonize_2d as skeletonize2d
        import alinea.phenomenal.segmentation_2d as segmentation_2d

        skeleton_1 = skeletonize2d.skeletonize_thinning(image)
        segmented = segmentation_2d.segment_organs_skeleton_image(skeleton_1)

        tools_test.show_image(image, str(angle))
        tools_test.show_image(skeleton_1, str(angle))
        tools_test.show_image(segmented, str(angle))

        # tools_test.show_comparison_3_image(image, skeleton_1, segmented)

def give_cube(organ, radius):
    cubes = list()

    for segment in organ.segments:
        for component in segment.component:
            for point in component:
                cube = reconstruction_3d.algo.Cube(point[0],
                                                   point[1],
                                                   point[2],
                                                   radius)

                cubes.append(cube)

    return cubes


def propagate_organs(cubes, organ):

    organ_cubes = list()
    new_cubes = list()

    print 'NB : ', len(organ.segments)
    # 7101

    i = 0
    for cube in cubes:
        ok = False
        for segment in organ.segments:
            for component in segment.component:
                for point in component:
                    if cube.position[0, 0] == point[0]:
                        if cube.position[0, 1] == point[1]:
                            if cube.position[0, 2] == point[2]:
                                organ_cubes.append(cube)
                                ok = True
        if ok is False:
            new_cubes.append(cube)

        print i
        i += 1

    return organ_cubes, new_cubes



#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_segmentation_3d()