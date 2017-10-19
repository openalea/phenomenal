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
import os

import cv2
import numpy

import openalea.deploy.shared_data
import alinea.phenomenal.binarization_post_processing
import alinea.phenomenal.binarization_routine
import alinea.phenomenal.configuration
import alinea.phenomenal.misc
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.calibration_model
import alinea.phenomenal.calibration_manual
import alinea.phenomenal.skeletonize_2d
import alinea.phenomenal.segmentation_2d
import alinea.phenomenal.plant_1
import alinea.phenomenal.viewer
from alinea.phenomenal.binarization_routine import (top_binarization_hsv,
                                            side_binarization_mean_shift)
from alinea.phenomenal.binarization_algorithm import get_mean_image


# ==============================================================================


def binarization(images):
    factor = alinea.phenomenal.configuration.\
        binarization_factor('factor_image_basic.cfg')

    if (-1) in images:
        top_image = images.pop((-1))
        mean_image = get_mean_image(images.values())
        images[(-1)] = top_image
    else:
        mean_image = get_mean_image(images.values())

    binarize_images = dict()
    for angle in images:
        if angle < 0:
            binarize_images[angle] = top_binarization_hsv(images[angle], factor)
        else:
            binarize_images[angle] = side_binarization_mean_shift(
                images[angle], mean_image, factor)

    return binarize_images


def binarization_post_processing(binarize_images):

    share_data_directory = openalea.deploy.shared_data. \
        shared_data(alinea.phenomenal)

    mask_path = os.path.join(share_data_directory, 'roi_stem.png')
    mask_image = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    post_processing_images = alinea.phenomenal. \
        binarization_post_processing. \
        remove_plant_support_from_images(binarize_images, mask=mask_image)

    return post_processing_images


def multi_view_reconstruction(binarize_images):

    radius = 5
    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.plant_1.\
        plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    images_selected = dict()
    for angle in binarize_images:
        if 0 <= angle <= 360:
            images_selected[angle] = binarize_images[angle]

    points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
        images_selected, projection, precision=radius, verbose=True)


    # Viewing
    alinea.phenomenal.viewer.show_points_3d(points_3d, scale_factor=2)

    return points_3d, radius


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

    images = alinea.phenomenal.misc.load_images(files, cv2.IMREAD_UNCHANGED)
    images_binarize = binarization(images)
    post_processing_images = binarization_post_processing(images_binarize)
    # points_3d, radius = multi_view_reconstruction(post_processing_images)

    # ==========================================================================

    angle_choose = 90

    # ==========================================================================

    skeleton_image = alinea.phenomenal.skeletonize_2d.skeletonize(
        post_processing_images[angle_choose], methods='thinning')

    stem, leaves, segments = alinea.phenomenal.segmentation_2d.\
        segment_organs_skeleton_image(skeleton_image)

    image = numpy.zeros(post_processing_images[angle_choose].shape)
    img = write_segmentation_on_image(stem, leaves, segments, image)

    alinea.phenomenal.viewer.show_image(post_processing_images[angle_choose])

    alinea.phenomenal.viewer.show_images(
        [images_binarize[angle_choose],
         post_processing_images[angle_choose],
         img],
        name_windows='Image & Segmentation : %d degree' % angle_choose)
    #
    # histogram = alinea.phenomenal.image.compute_inclination(
    #     stem.segments)
    #
    #     pylab.hist(histogram, 180, histtype='bar', rwidth=0.8)
    #     pylab.show()

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../local/data_set_0962_A310_ARCH2013-05-13/')
