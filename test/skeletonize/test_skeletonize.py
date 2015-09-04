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
import cv2
import glob
import matplotlib
import pylab as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#       =======================================================================
#       Local Import
import alinea.phenomenal.skeletonize as skeletonize
import alinea.phenomenal.repair_processing as repair_processing
import alinea.phenomenal.segmentation as segmentation
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.calibration_tools as calibration_tools
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
from phenomenal.test import tools_test

#       =======================================================================
#       Code

def compute_my_random_color_map():
    cdict = dict()
    cdict['red'] = ((0., 0., 0.),)
    cdict['green'] = ((0., 0., 0.),)
    cdict['blue'] = ((0., 0., 0.),)
    import random

    def random_color(i):
        return ((float(i / 100.0),
                 random.uniform(0.1, 1.0),
                 random.uniform(0.1, 1.0)),)

    for i in range(0, 100):
        cdict['red'] = cdict['red'] + random_color(i)
        cdict['green'] = cdict['green'] + random_color(i)
        cdict['blue'] = cdict['blue'] + random_color(i)

    cdict['red'] = cdict['red'] + ((1, 1, 1),)
    cdict['green'] = cdict['green'] + ((1, 1, 1),)
    cdict['blue'] = cdict['blue'] + ((1, 1, 1),)

    my_random_color_map = matplotlib.colors.LinearSegmentedColormap(
        'my_colormap', cdict, 256)

    return my_random_color_map


def show_image_and_skeleton(image, skeleton):

    my_random_color_map = compute_my_random_color_map()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    ax1.imshow(image, cmap=my_random_color_map, interpolation='nearest')
    ax1.axis('off')

    ax2.imshow(skeleton, cmap=my_random_color_map, interpolation='nearest')
    # ax2.contour(image, [0.5], colors='w')
    ax2.axis('off')

    fig.subplots_adjust(
        hspace=0.01, wspace=0.01, top=1, bottom=0, left=0, right=1)

    plt.show()


def test_skeletonize():
    data_directory = "../../local/data/tests/Samples_binarization_2/"
    files = glob.glob(data_directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)

    for angle in images:

        image_repair = repair_processing.fill_up_prop(images[angle])
        skeleton = skeletonize.skeletonize_image_skimage(image_repair)

        # kernel = np.ones((5, 5), np.uint8)
        # skeleton = cv2.dilate(skeleton, kernel, iterations=4)

        tools_test.show_comparison_2_image(images[angle], skeleton)

        cv2.imwrite("../../local/data/refs/test_skeletonize/" +
                    "ref_skeletonize_%d.png" % angle, skeleton)


def test_segmentation():
    data_directory = "../../local/data/tests/Samples_binarization_7/"
    files = glob.glob(data_directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)

    for angle in images:
        image_repair = repair_processing.fill_up_prop(images[angle])

        skeleton = skeletonize.skeletonize_image_skimage(image_repair)
        skeleton = segmentation.segment_organs_skeleton_image(skeleton)

        show_image_and_skeleton(images[angle], skeleton)


def have_connected_position(position, segments):

    i = 0
    kseg = None
    num = None
    for seg in segments:
        position_1, position_2 = seg

        if position_1 == position:
            i += 1
            num = 1
            kseg = seg

        if position_2 == position:
            i += 1
            num = 0
            kseg = seg

    if i == 1:
        return num, kseg
    else:
        return None, None


def have_connected_position_to_segments(position, segments_list, my_seg):

    for segment in segments_list:
        if my_seg is not segment:
            for pos in segment:
                if pos == position:
                    return True
    return False


def plot_skeleton_3d(segments):

    segments_list = list()

    while segments:
        segment = segments.pop()

        my_seg = list()
        my_seg.append(segment[0])
        my_seg.append(segment[1])

        my_seg_tmp = list()
        my_seg_tmp.append(segment[0])
        my_seg_tmp.append(segment[1])

        while my_seg_tmp:
            position = my_seg_tmp.pop()

            num, seg = have_connected_position(position, segments)
            if seg is not None:

                if not have_connected_position_to_segments(position,
                                                    segments_list,
                                                    my_seg):

                    my_seg_tmp.append(seg[num])
                    my_seg.append(seg[num])
                    segments.remove(seg)

        segments_list.append(my_seg)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    print "lenght : ", len(segments_list)
    for ii in range(len(segments_list) -1, 0, -1):
        segment = segments_list[ii]
        x = list()
        y = list()
        z = list()

        for position in segment:
            x.append(position[0])
            y.append(position[1])
            z.append(position[2])
            ax.scatter(position[0], position[1], position[2])

        ax.plot(x, y, z, label='parametric curve')

    plt.show()

    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    #
    # for position_1, position_2 in segments:
    #     ax.plot([position_1[0], position_2[0]],
    #             [position_1[1], position_2[1]],
    #             [position_1[2], position_2[2]], label='parametric curve')
    #
    # plt.show()


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
        angle = angles[i]

        if angle < 105:
            images[angle] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    #   ========================================================================

    opencv_calibration = calibration_chessboard.Calibration.read_calibration(
        'calibration')

    image_0_90 = dict()
    for angle in images:
        if angle <= 105:
            image_0_90[angle] = images[angle]

    opencv_cubes = reconstruction_3d.reconstruction_3d(
        images, opencv_calibration, 5)
    #
    # tools_test.show_cube(opencv_cubes, 10, "opencv_cubes")

    # skeletonize.skeletonize_3d_transform_distance(opencv_cubes)
    #
    # skeletonize.test_skeletonize_3d(opencv_cubes, 10)

    skeleton_3d = skeletonize.skeletonize_3d_xu_method(opencv_cubes, 10)

    plot_skeleton_3d(skeleton_3d)


#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    # test_skeletonize()
    # test_segmentation()

    test_skeletonize_3d()
