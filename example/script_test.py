# -*- python -*-
#
#       script_test.py : 
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
import cv2
import numpy

#       ========================================================================
#       Local Import
import alinea.phenomenal.repair_processing
import alinea.phenomenal.binarization
import alinea.phenomenal.configuration
import alinea.phenomenal.misc
# import alinea.phenomenal.result_viewer
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.calibration_jerome
import alinea.phenomenal.calibration_manual
import alinea.phenomenal.skeletonize_2d
import alinea.phenomenal.segmentation_2d

#       ========================================================================
#       Code

def write_segmentation_on_image(stem, leaves, segments, skeleton_image):

    # Write if number on pixel image:
    for segment in segments:
        for y, x in segment.points:
            skeleton_image[y, x] = segment.id_number

    for segment in stem.segments:
        for y, x in segment.points:
            skeleton_image[y, x] = 255

    for leaf in leaves:
        for segment in leaf.segments:
            for y, x in segment.points:
                skeleton_image[y, x] = leaf.id_number

    skeleton_image = skeleton_image.astype(numpy.uint8)

    return skeleton_image


def run_example(data_directory):
    pot_ids = alinea.phenomenal.misc.load_files(data_directory)

    files = pot_ids['0962']['2013-05-24']

    # for pot_id in pot_ids:
    #     for date in pot_ids[pot_id]:

    # files = pot_ids[pot_id][date]

    images = alinea.phenomenal.misc.load_images(
        files, cv2.IMREAD_UNCHANGED)

    #   ================================================================

    images_binarize = example_binarization_mean_shift(images)

    #   ================================================================

    repair_images = example_repair_processing(images_binarize)

    #   ================================================================
    #
    # calibration = alinea.phenomenal.calibration_jerome. \
    #     Calibration.read_calibration('./calibration/fitted_result',
    #                                  file_is_in_share_directory=False)

    calibration = alinea.phenomenal.calibration_manual.Calibration()

    images_selected = dict()
    for angle in repair_images:
        if -1 <= angle <= 360:
            images_selected[angle] = repair_images[angle]

    points_3d = alinea.phenomenal.multi_view_reconstruction. \
        reconstruction_3d(images_selected,
                          calibration,
                          precision=4,
                          verbose=True)

    # print pot_id, date
    # alinea.phenomenal.result_viewer.show_points_3d(points_3d,
    #                                                scale_factor=2)

    #   ========================================================================

    angle_choose = 90

    #   ========================================================================

    skeleton_image = alinea.phenomenal.skeletonize_2d.skeletonize(
        images_selected[angle_choose], methods='thinning')

    stem, leaves, segments = alinea.phenomenal.segmentation_2d.\
        segment_organs_skeleton_image(skeleton_image)

        # image = numpy.zeros(images[angle].shape)
        #
        # img = write_segmentation_on_image(stem,
        #                                   leaves,
        #                                   segments,
        #                                   image)
        #
        # alinea.phenomenal.result_viewer.show_images(
        #     [images[angle], img],
        #     name_windows='Image & Segmentation : %d degree' % angle,
        #     names_axes=['Image', 'Segmentation'],
        #     color_map_axes=[matplotlib.cm.binary,
        #                     compute_my_random_color_map()])

    histogram = alinea.phenomenal.segmentation_2d.compute_inclination(
        stem.segments)

        # pylab.hist(histogram, 180, histtype='bar', rwidth=0.8)
        # pylab.show()


def example_binarization_mean_shift(images):

    factor_side_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'configuration_image_basic.cfg')

    factor_top_binarization = \
        alinea.phenomenal.configuration.binarization_factor(
            'configuration_top_image.cfg')

    top_image = images.pop(-1)
    mean_image = alinea.phenomenal.binarization.get_mean_image(images.values())
    images[-1] = top_image

    images_binarize = dict()
    for angle in images:

        if angle == -1:
            images_binarize[angle] = \
                alinea.phenomenal.binarization.binarization(
                    images[angle],
                    factor_top_binarization,
                    is_top_image=True,
                    methods='hsv')
        else:
            images_binarize[angle] = \
                alinea.phenomenal.binarization.binarization(
                    images[angle],
                    factor_side_binarization,
                    methods='mean_shift',
                    mean_image=mean_image)

    return images_binarize


def example_repair_processing(images):

    repair_images = dict()
    for angle in images:
        if angle == -1:
            repair_images[angle] = alinea.phenomenal.repair_processing.\
                fill_up_prop(images[angle], is_top_image=True)
        else:
            repair_images[angle] = alinea.phenomenal.repair_processing.\
                fill_up_prop(images[angle])

    return repair_images


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../local/data_set_0962_A310_ARCH2013-05-13/')
