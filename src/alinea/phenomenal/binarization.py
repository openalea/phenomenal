# -*- python -*-
#
#       binarization.py : Functions call for binarization img color -> img bin
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
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

""" Binarization routines for PhenoArch/ images """

#       ========================================================================
#       External Import
import numpy
import cv2

#       ========================================================================
#       Local Import
import openalea.opencv.extension as ocv2
import alinea.phenomenal.repair_processing as repair_processing
import alinea.phenomenal.binarization_algorithm as b_algorithm

#       ========================================================================


def side_binarization_hsv(image, configuration):
    """
    Binarization of side image for Lemnatech cabin based on hsv segmentation.

    Based on Michael pipeline
    :param image: BGR image
    :param configuration: Object BinarizationConfig
    :return: Binary image
    """

    # elementMorph = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    c = configuration.cubicle_domain
    image_cropped = image[c[0]:c[1], c[2]:c[3]]
    hsv_image = ocv2.bgr2hsv(image_cropped)

    #   =======================================================================
    #   Main area segmentation
    main_area_seg = cv2.medianBlur(hsv_image, ksize=9)
    main_area_seg = cv2.inRange(main_area_seg,
                                configuration.roi_main.hsv_min,
                                configuration.roi_main.hsv_max)

    main_area_seg = ocv2.dilate(main_area_seg, iterations=2)
    main_area_seg = ocv2.erode(main_area_seg, iterations=2)

    mask_cropped = configuration.roi_main.mask[c[0]:c[1], c[2]:c[3]]
    main_area_seg = cv2.bitwise_and(main_area_seg,
                                    main_area_seg,
                                    mask=mask_cropped)

    #   =======================================================================
    #   Band area segmentation
    background_cropped = configuration.background[c[0]:c[1], c[2]:c[3]]
    hsv_background = ocv2.bgr2hsv(background_cropped)
    grayscale_background = hsv_background[:, :, 0]

    grayscale_image = hsv_image[:, :, 0]

    band_area_seg = cv2.subtract(grayscale_image, grayscale_background)
    retval, band_area_seg = cv2.threshold(band_area_seg,
                                          122,
                                          255,
                                          cv2.THRESH_BINARY)

    mask_cropped = configuration.roi_orange_band.mask[c[0]:c[1], c[2]:c[3]]
    band_area_seg = cv2.bitwise_and(band_area_seg,
                                    band_area_seg,
                                    mask=mask_cropped)

    band_area_seg = ocv2.erode(band_area_seg, iterations=5)
    band_area_seg = ocv2.dilate(band_area_seg, iterations=5)

    #   =======================================================================
    #   Pot area segmentation
    pot_area_seg = cv2.inRange(hsv_image,
                               configuration.roi_pot.hsv_min,
                               configuration.roi_pot.hsv_max)

    mask_cropped = configuration.roi_pot.mask[c[0]:c[1], c[2]:c[3]]
    pot_area_seg = cv2.bitwise_and(pot_area_seg,
                                   pot_area_seg,
                                   mask=mask_cropped)

    #   =======================================================================
    #   Full segmented image
    image_seg = cv2.add(main_area_seg, band_area_seg)
    image_seg = cv2.add(image_seg, pot_area_seg)

    image_out = numpy.zeros([image.shape[0], image.shape[1]], 'uint8')
    image_out[c[0]:c[1], c[2]:c[3]] = image_seg

    return image_out


def side_binarization(image, mean_image, configuration):
    """
    Binarization of side image based on mean shift difference

    :param image: BGR image
    :param mean_image: Mean image
    :param configuration: Object BinarizeConfiguration
    :return: Binary image
    """
    roi_main = configuration.roi_main

    mask = cv2.add(roi_main.mask,
                   configuration.roi_orange_band.mask)

    mask = cv2.add(mask,
                   configuration.roi_panel.mask)

    result = b_algorithm.mixed_binarization(
        image,
        mean_image,
        configuration.roi_main.hsv_min,
        configuration.roi_main.hsv_max,
        configuration.meanshift_binarization_factor.threshold,
        configuration.meanshift_binarization_factor.dark_background,
        mask,
        configuration.roi_main.mask)

    mask_clean_noise = cv2.add(configuration.roi_orange_band.mask,
                               configuration.roi_panel.mask)

    result = repair_processing.clean_noise(result, mask_clean_noise)

    return result


def side_binarization_elcom(image, mean_image, configuration):
    """
    Binarization of side image based on mean shift difference

    :param image: BGR image
    :param mean_image: Mean image
    :param configuration: Object BinarizeConfiguration
    :return: Binary image
    """

    result = b_algorithm.mixed_binarization(
        image,
        mean_image,
        configuration.roi_stem.hsv_min,
        configuration.roi_stem.hsv_max,
        configuration.meanshift_binarization_factor.threshold,
        configuration.meanshift_binarization_factor.dark_background,
        configuration.roi_main.mask,
        configuration.roi_stem.mask)

    result = cv2.medianBlur(result, 3)

    return result


def side_binarization_adaptive_thresh(image, configuration):
    """
    Binarization of side image based on adaptive theshold algorithm of cv2

    :param image: BGR image
    :param configuration: Object BinarizeConfiguration
    :return: Binary image
    """
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    result1 = b_algorithm.adaptive_thresh_mean_c(
        img,
        41,
        20,
        mask=configuration.roi_main.mask)

    result2 = b_algorithm.adaptive_thresh_mean_c(
        img,
        399,
        45,
        mask=configuration.roi_main.mask)

    result3 = b_algorithm.adaptive_thresh_gaussian_c(
        img,
        41,
        20,
        mask=configuration.roi_main.mask)

    result = cv2.add(result1, result2)
    result = cv2.add(result, result3)

    return result


def top_binarization_hsv(image, configuration):
    """
    Binarization of top image for Lemnatech cabin based on hsv segmentation.

    :param image: BGR image
    :param configuration: Object BinarizeConfiguration
    :return: Binary image
    """
    configuration.print_value()

    # c = configuration.cubicle_domain
    # image_cropped = image[c[0]:c[1], c[2]:c[3]]
    hsv_image = ocv2.bgr2hsv(image)

    #   =======================================================================
    #   Main area segmentation
    main_area_seg = cv2.medianBlur(hsv_image, ksize=9)
    main_area_seg = cv2.inRange(main_area_seg,
                                configuration.roi_main.hsv_min,
                                configuration.roi_main.hsv_max)

    main_area_seg = ocv2.dilate(main_area_seg, iterations=2)
    main_area_seg = ocv2.erode(main_area_seg, iterations=2)
    #
    # mask_cropped = configuration.roi_main.mask[c[0]:c[1], c[2]:c[3]]
    # main_area_seg = cv2.bitwise_and(main_area_seg,
    #                                 main_area_seg,
    #                                 mask=mask_cropped)

    # image_out = numpy.zeros([image.shape[0], image.shape[1]], 'uint8')
    # image_out[c[0]:c[1], c[2]:c[3]] = main_area_seg

    return main_area_seg


def get_mean_image(images):
    """
    Compute the mean image of image list.

    :param images: A list containing the images.
    :return: A image who is the mean of the list image
    """
    length = len(images)
    weight = 1. / length

    start = cv2.addWeighted(images[0], weight, images[1], weight, 0)

    function = lambda x, y: cv2.addWeighted(x, 1, y, weight, 0)

    return reduce(function, images[2:], start)
