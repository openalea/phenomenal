# -*- python -*-
# -*- coding:utf-8 -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
""" Binarization routines for binarize image """
# ==============================================================================
import numpy
import cv2

from alinea.phenomenal.binarization_post_processing import (
    erode_dilate,
    dilate_erode)

from alinea.phenomenal.binarization_algorithm import (
    threshold_meanshift,
    threshold_hsv)
# ==============================================================================


def meanshift_hsv(image,
                  mean_image,
                  threshold=0.3,
                  dark_background=False,
                  hsv_min=(30, 11, 0),
                  hsv_max=(129, 254, 141),
                  mask_mean_shift=None,
                  mask_hsv=None,
                  mask_clean_noise=None):

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    binary_hsv_image = threshold_hsv(hsv_image, hsv_min, hsv_max, mask_hsv)

    binary_mean_shift_image = threshold_meanshift(
        image, mean_image, threshold, dark_background, mask_mean_shift)

    result = cv2.add(binary_hsv_image, binary_mean_shift_image * 255)

    result = erode_dilate(result, iterations=3, mask=mask_clean_noise)
    result = erode_dilate(result, iterations=1)

    return result


def meanshift_hsv_elcom(image,
                        mean_image,
                        threshold=0.3,
                        dark_background=False,
                        hsv_min=(30, 25, 0),
                        hsv_max=(150, 254, 165),
                        mask_mean_shift=None,
                        mask_hsv=None):

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    binary_hsv_image = threshold_hsv(hsv_image, hsv_min, hsv_max, mask_hsv)

    binary_mean_shift_image = threshold_meanshift(
        image, mean_image, threshold, dark_background, mask_mean_shift)

    result = cv2.add(binary_hsv_image, binary_mean_shift_image * 255)

    result = cv2.medianBlur(result, 3)

    return result


def roi_hsv(image,
            cubicle_domain,
            cubicle_background,
            main_hsv_min,
            main_hsv_max,
            main_mask,
            orange_band_mask,
            pot_hsv_min,
            pot_hsv_max,
            pot_mask):
    """
    Binarization of side image for Lemnatech cabin based on hsv segmentation.

    Based on Michael pipeline
    """
    # elementMorph = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')

    if image.ndim != 3:
        raise ValueError('image should be 3D array')
    # ==========================================================================

    c = cubicle_domain
    image_cropped = image[c[0]:c[1], c[2]:c[3]]
    hsv_image = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2HSV)

    # ==========================================================================
    # Main area segmentation
    main_area_seg = cv2.medianBlur(hsv_image, ksize=9)
    main_area_seg = cv2.inRange(main_area_seg, main_hsv_min, main_hsv_max)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    main_area_seg = cv2.dilate(main_area_seg, element, iterations=2)
    main_area_seg = cv2.erode(main_area_seg, element, iterations=2)

    mask_cropped = main_mask[c[0]:c[1], c[2]:c[3]]
    main_area_seg = cv2.bitwise_and(main_area_seg,
                                    main_area_seg,
                                    mask=mask_cropped)

    # ==========================================================================
    # Band area segmentation
    background_cropped = cubicle_background[c[0]:c[1], c[2]:c[3]]
    hsv_background = cv2.cvtColor(background_cropped, cv2.COLOR_BGR2HSV)
    grayscale_background = hsv_background[:, :, 0]

    grayscale_image = hsv_image[:, :, 0]

    band_area_seg = cv2.subtract(grayscale_image, grayscale_background)
    retval, band_area_seg = cv2.threshold(band_area_seg,
                                          122,
                                          255,
                                          cv2.THRESH_BINARY)

    mask_cropped = orange_band_mask[c[0]:c[1], c[2]:c[3]]
    band_area_seg = cv2.bitwise_and(band_area_seg,
                                    band_area_seg,
                                    mask=mask_cropped)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    band_area_seg = cv2.dilate(band_area_seg, element, iterations=5)
    band_area_seg = cv2.erode(band_area_seg, element, iterations=5)

    # ==========================================================================
    # Pot area segmentation
    pot_area_seg = cv2.inRange(hsv_image, pot_hsv_min, pot_hsv_max)

    mask_cropped = pot_mask[c[0]:c[1], c[2]:c[3]]
    pot_area_seg = cv2.bitwise_and(pot_area_seg,
                                   pot_area_seg,
                                   mask=mask_cropped)

    # ==========================================================================
    # Full segmented image
    image_seg = cv2.add(main_area_seg, band_area_seg)
    image_seg = cv2.add(image_seg, pot_area_seg)

    image_out = numpy.zeros([image.shape[0], image.shape[1]], 'uint8')
    image_out[c[0]:c[1], c[2]:c[3]] = image_seg

    return image_out


def line_adaptive_threshold(image, mask):
    """
    Binarization of side image based on adaptive threshold algorithm of cv2
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')
    if image.ndim != 3:
        raise ValueError('image should be 3D array')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('image should be 2D array')

        if image.shape[0:2] != mask.shape:
            raise ValueError('image and mask should have the same shape')
    # ==========================================================================

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if mask is not None:
        img = cv2.bitwise_and(img, img, mask=mask)

    block_size, c = (41, 20)
    result1 = cv2.adaptiveThreshold(img,
                                    255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY_INV,
                                    block_size,
                                    c)

    block_size, c = (399, 45)
    result2 = cv2.adaptiveThreshold(img,
                                    255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY_INV,
                                    block_size,
                                    c)

    block_size, c = (41, 20)
    result3 = cv2.adaptiveThreshold(img,
                                    255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV,
                                    block_size,
                                    c)

    result = cv2.add(result1, result2)
    result = cv2.add(result, result3)

    if mask is not None:
        result = cv2.bitwise_and(result, result, mask=mask)

    return result


def blur_hsv_erode_dilate(image, hsv_min, hsv_max,
                          median_blur_size=9,
                          iterations=5,
                          mask=None):
    """
    Binarization of top image for Lemnatech cabin based on hsv segmentation.
    """
    # ==========================================================================
    # Check Parameters
    if not isinstance(image, numpy.ndarray):
        raise TypeError('image should be a numpy.ndarray')
    if image.ndim != 3:
        raise ValueError('image should be 3D array')

    if not isinstance(hsv_min, tuple):
        raise TypeError('hsv_min should be a Tuple')
    if len(hsv_min) != 3:
        raise ValueError('hsv_min should be of size 3')
    for value in hsv_min:
        if not isinstance(value, int):
            raise ValueError('hsv_min value should be a integer')

    if not isinstance(hsv_max, tuple):
        raise TypeError('hsv_max should be a Tuple')
    if len(hsv_max) != 3:
        raise ValueError('hsv_max should be of size 3')
    for value in hsv_max:
        if not isinstance(value, int):
            raise ValueError('hsv_max value should be a integer')

    if mask is not None:
        if not isinstance(mask, numpy.ndarray):
            raise TypeError('mask should be a numpy.ndarray')
        if mask.ndim != 2:
            raise ValueError('mask should be 2D array')
        if image.shape[0:2] != mask.shape:
            raise ValueError('image and mask should have the same shape')
    # ==========================================================================

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_image = cv2.medianBlur(hsv_image, ksize=median_blur_size)

    bin_img = threshold_hsv(hsv_image, hsv_min, hsv_max, mask=mask)

    bin_img = dilate_erode(bin_img,
                           kernel_shape=(3, 3),
                           iterations=iterations,
                           mask=mask)

    return bin_img
