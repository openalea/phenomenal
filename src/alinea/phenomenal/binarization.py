# -*- python -*-
# -*- coding:utf-8 -*-
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
import sys
import numpy
import cv2

import alinea.phenomenal.opencv_wrapping as ocv2


#       ========================================================================
#       Local Import

import alinea.phenomenal.binarization_post_processing
import alinea.phenomenal.binarization_algorithm


#       ========================================================================

def binarization(images, factor, methods='mean_shift', emptiesTop=None):
    try:
        if methods == 'mean_shift' or methods == 'elcom':
            mean_image = get_mean_image(images['side'].values())
            if mean_image is None:
                return None

        binarize_images = dict([('top',dict()), ('side', dict())])
        for angle in images['top']:
            if methods == 'elcom':
                binarize_images['top'][angle] = top_binarization_elcom(
                    images['top'][angle], factor, emptiesTop)
            else:
                binarize_images['top'][angle] = top_binarization_hsv(
                    images['top'][angle], factor)

        for angle in images['side']:
            if methods == 'mean_shift':
                binarize_images['side'][angle] = side_binarization_mean_shift(
                    images['side'][angle], mean_image, factor)
            if methods == 'hsv':
                binarize_images['side'][angle] = side_binarization_hsv(
                    images['side'][angle], factor)
            if methods == 'elcom':
                binarize_images['side'][angle] = side_binarization_elcom(
                    images['side'][angle], mean_image, factor)
            if methods == 'adaptive_threshold':
                binarize_images['side'][angle] = side_binarization_adaptive_thresh(
                    images['side'][angle], factor)

    except cv2.error, e:
        sys.stderr.write("OpenCvError - " + methods + " : " + str(e) + "\n")
        return None
    except TypeError, e:
        sys.stderr.write("TypeError - " + methods + " : " + str(e) + "\n")
        return None
    except Exception, e:
        sys.stderr.write("Error - " + methods + " : " + str(e) + "\n")
        return None
    
    return binarize_images


def side_binarization_hsv(image, factor):
    """
    Binarization of side image for Lemnatech cabin based on hsv segmentation.
    
    Based on Michael pipeline
    :param image: BGR image
    :param factor: Object BinarizationConfig
    :return: Binary image
    """  # elementMorph = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    
    c = factor.side_cubicle_domain
    image_cropped = image[c[0]:c[1], c[2]:c[3]]
    hsv_image = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2HSV)
    
    #   =======================================================================
    #   Main area segmentation
    main_area_seg = cv2.medianBlur(hsv_image, ksize=9)
    main_area_seg = cv2.inRange(main_area_seg,
                                factor.side_roi_main.hsv_min,
                                factor.side_roi_main.hsv_max)
    
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    main_area_seg = cv2.dilate(main_area_seg, element, iterations=2)
    main_area_seg = cv2.erode(main_area_seg, element, iterations=2)

    mask_cropped = factor.side_roi_main.mask[c[0]:c[1], c[2]:c[3]]
    main_area_seg = cv2.bitwise_and(main_area_seg,
                                    main_area_seg,
                                    mask=mask_cropped)
    
    #   =======================================================================
    #   Band area segmentation
    background_cropped = factor.side_cubicle_background[c[0]:c[1], c[2]:c[3]]
    hsv_background = cv2.cvtColor(background_cropped, cv2.COLOR_BGR2HSV)
    grayscale_background = hsv_background[:, :, 0]
    
    grayscale_image = hsv_image[:, :, 0]
    
    band_area_seg = cv2.subtract(grayscale_image, grayscale_background)
    retval, band_area_seg = cv2.threshold(band_area_seg,
                                          122,
                                          255,
                                          cv2.THRESH_BINARY)
    
    mask_cropped = factor.side_roi_orange_band.mask[c[0]:c[1], c[2]:c[3]]
    band_area_seg = cv2.bitwise_and(band_area_seg,
                                    band_area_seg,
                                    mask=mask_cropped)
    
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    band_area_seg = cv2.dilate(band_area_seg, element, iterations=5)
    band_area_seg = cv2.erode(band_area_seg, element, iterations=5)
    
    #   =======================================================================
    #   Pot area segmentation
    pot_area_seg = cv2.inRange(hsv_image,
                               factor.side_roi_pot.hsv_min,
                               factor.side_roi_pot.hsv_max)
    
    mask_cropped = factor.side_roi_pot.mask[c[0]:c[1], c[2]:c[3]]
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


def top_binarization_hsv(image, factor):
    """
    Binarization of top image for Lemnatech cabin based on hsv segmentation.
    
    :param image: BGR image
    :param factor: Object BinarizeConfiguration
    :return: Binary image
    """
    # c = factor.top_cubicle_domain
    # image_cropped = image[c[0]:c[1], c[2]:c[3]]
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    #   =======================================================================
    #   Main area segmentation
    main_area_seg = cv2.medianBlur(hsv_image, ksize=9)
    main_area_seg = cv2.inRange(main_area_seg,
                                factor.top_roi_main.hsv_min,
                                factor.top_roi_main.hsv_max)
    
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    main_area_seg = cv2.dilate(main_area_seg, element, iterations=5)
    main_area_seg = cv2.erode(main_area_seg, element, iterations=5)
    
    # mask_cropped = factor.top_roi_main.mask[c[0]:c[1], c[2]:c[3]]
    # main_area_seg = cv2.bitwise_and(main_area_seg,
    #                                 main_area_seg,
    #                                 mask=mask_cropped)
    
    # image_out = numpy.zeros([image.shape[0], image.shape[1]], 'uint8')
    # image_out[c[0]:c[1], c[2]:c[3]] = main_area_seg

    return main_area_seg


def get_mean_image(images):
    """
    Compute the mean image of a image list.
    
    :param images: A list images.
    :return: A image who is the mean of the list image
    """
    try:
        if isinstance(images, (list, tuple)):
            length = len(images)
            weight = 1. / length
            
            start = cv2.addWeighted(images[0], weight, images[1], weight, 0)
            
            function = lambda x, y: cv2.addWeighted(x, 1, y, weight, 0)
            
            return reduce(function, images[2:], start)
        else:
            sys.stderr.write("TypeError - get_mean_image : "
                             "Require list argument\n")
            return None
    
    except cv2.error, e:
        sys.stderr.write("OpenCvError - get_mean_image : " + str(e) + "\n")
        return None
    except TypeError, e:
        sys.stderr.write("TypeError - get_mean_image : " + str(e) + "\n")
        return None
    except Exception, e:
        sys.stderr.write("Error - get_mean_image : " + str(e) + "\n")
        return None

    
def side_binarization_mean_shift(image, mean_image, factor):
    """
    Binarization of side image based on mean shift difference
    
    :param image: BGR image
    :param mean_image: Mean image
    :param factor: Object BinarizeConfiguration
    :return: Binary image
    """
    
    mask = cv2.add(factor.side_roi_main.mask,
                   factor.side_roi_orange_band.mask)
    
    mask = cv2.add(mask, factor.side_roi_panel.mask)
    
    result = alinea.phenomenal.binarization_algorithm.mixed_binarization(
        image,
        mean_image,
        factor.side_roi_main.hsv_min,
        factor.side_roi_main.hsv_max,
        factor.mean_shift_binarization_factor.threshold,
        factor.mean_shift_binarization_factor.dark_background,
        mask,
        factor.side_roi_main.mask)
    
    mask_clean_noise = cv2.add(factor.side_roi_orange_band.mask,
                               factor.side_roi_panel.mask)

    result = alinea.phenomenal.binarization_post_processing.clean_noise(
        result, mask_clean_noise)
    
    return result


def side_binarization_elcom(image, mean_image, factor):
    """
    Binarization of side image based on mean shift difference
    
    :param image: BGR image
    :param mean_image: Mean image
    :param factor: Object BinarizeConfiguration
    :return: Binary image
    """
    
    result = alinea.phenomenal.binarization_algorithm.mixed_binarization(
        image,
        mean_image,
        factor.side_roi_stem.hsv_min,
        factor.side_roi_stem.hsv_max,
        float(factor.mean_shift_binarization_factor.threshold),
        factor.mean_shift_binarization_factor.dark_background,
        factor.side_roi_main.mask,
        factor.side_roi_stem.mask)
    
    result = cv2.medianBlur(result, 3)
    
    return result


def side_binarization_adaptive_thresh(image, factor):
    """
    Binarization of side image based on adaptive theshold algorithm of cv2
    
    :param image: BGR image
    :param factor: Object BinarizeConfiguration
    :return: Binary image
    """
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    result1 = alinea.phenomenal.binarization_algorithm.\
        adaptive_thresh_mean_c(img, 41, 20, mask=factor.side_roi_main.mask)
    
    result2 = alinea.phenomenal.binarization_algorithm.\
        adaptive_thresh_mean_c(img, 399, 45, mask=factor.side_roi_main.mask)
    
    result3 = alinea.phenomenal.binarization_algorithm.\
        adaptive_thresh_gaussian_c(img, 41, 20, mask=factor.side_roi_main.mask)
    
    result = cv2.add(result1, result2)
    result = cv2.add(result, result3)
    
    return result

def top_binarization_elcom(bgr, factor, emptiesTop, useEmpty=True):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    luv = cv2.cvtColor(bgr, cv2.COLOR_BGR2LUV)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    hls = cv2.cvtColor(bgr, cv2.COLOR_BGR2HLS)
    xyz = cv2.cvtColor(bgr, cv2.COLOR_BGR2XYZ)
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

    mask_pot = factor.top_cubicle.mask_pot
    mask_rails = factor.top_cubicle.mask_rails

    if factor.General.cabin == 5:
        if useEmpty:
            emptyImg = emptiesTop[0]
        imageBinSeuil = numpy.uint8( \
                    numpy.bitwise_or( \
                        numpy.bitwise_and( lab[:,:,1]>=120.5, \
                            numpy.bitwise_or( \
                                numpy.bitwise_and(lab[:,:,2]<139.5, \
                                    numpy.bitwise_or( \
                                        numpy.bitwise_and(lab[:,:,1]>=122.5, \
                                            numpy.bitwise_and(lab[:,:,1]<123.5, \
                                                numpy.bitwise_and(bgr[:,:,0] < 91.5, \
                                                    numpy.bitwise_and(hsv[:,:,1] >= 28.5, \
                                                        numpy.bitwise_and(yuv[:,:,0] >= 52.5, \
                                                            numpy.bitwise_or(luv[:,:,1] < 94.5, \
                                                                numpy.bitwise_and(luv[:,:,1] >= 94.5, bgr[:,:,2]>= 82.5) \
                                                            ) \
                                                        ) \
                                                    ) \
                                                ) \
                                            ) \
                                        ),
                                        numpy.bitwise_and(lab[:,:,1]<122.5, \
                                            numpy.bitwise_or(xyz[:,:,2] < 103.5, \
                                                numpy.bitwise_and(xyz[:,:,2] >= 103.5, \
                                                    numpy.bitwise_and(xyz[:,:,2] < 114.5, lab[:,:,1] < 121.5) \
                                                ) \
                                            ) \
                                        ) \
                                    ) \
                                ), \
                                numpy.bitwise_and(lab[:,:,2]>=139.5, \
                                    numpy.bitwise_or( \
                                        numpy.bitwise_and(hsv[:,:,1] < 55.5, \
                                            numpy.bitwise_and(bgr[:,:,0] < 143.5, bgr[:,:,2] < 110.5) \
                                        ), \
                                        numpy.bitwise_and(hsv[:,:,1] >= 55.5, \
                                            numpy.bitwise_and(xyz[:,:,2]>=56.5, \
                                                numpy.bitwise_or( \
                                                    numpy.bitwise_and(hsv[:,:,1]< 69.5, \
                                                        numpy.bitwise_or(hsv[:,:,0] >= 32.5, \
                                                            numpy.bitwise_and(hsv[:,:,0] < 32.5, \
                                                                numpy.bitwise_and(hsv[:,:,1]>= 61.5, \
                                                                    numpy.bitwise_or(numpy.bitwise_and(hsv[:,:,0] <= 20.5, xyz[:,:,2] < 138.5), \
                                                                        numpy.bitwise_and(hsv[:,:,0] < 20.5, \
                                                                            numpy.bitwise_or(lab[:,:,1] < 121.5, \
                                                                                numpy.bitwise_and(lab[:,:,1] >= 121.5, \
                                                                                    numpy.bitwise_or(luv[:,:,1] < 97.5, \
                                                                                        numpy.bitwise_and(luv[:,:,1] >= 97.5, \
                                                                                            numpy.bitwise_and(yuv[:,:,1] >= 134.5, yuv[:,:,1] < 137.5) \
                                                                                        ) \
                                                                                    ) \
                                                                                ) \
                                                                            ) \
                                                                        ) \
                                                                    ) \
                                                                ) \
                                                            ) \
                                                        ) \
                                                    ), \
                                                    numpy.bitwise_and(hsv[:,:,1]>= 69.5, \
                                                        numpy.bitwise_or( \
                                                            numpy.bitwise_and(bgr[:,:,1] < 84.5, \
                                                                numpy.bitwise_or(yuv[:,:,1] < 129.5, yuv[:,:,1] >= 135.5) \
                                                            ), \
                                                            numpy.bitwise_and(bgr[:,:,1] >= 84.5, \
                                                                numpy.bitwise_or( \
                                                                    numpy.bitwise_and(hsv[:,:,1] < 85.5, yuv[:,:,1]<143.5), \
                                                                    numpy.bitwise_and(hsv[:,:,1] >= 85.5, lab[:,:,1]<151.5) \
                                                                ) \
                                                            ) \
                                                        ) \
                                                    ) \
                                                ) \
                                            ) \
                                        ) \
                                    ) \
                                ) \
                            ) \
                        ), \
                        numpy.bitwise_and( lab[:,:,1]<120.5, \
                            numpy.bitwise_or( bgr[:,:,0] < 127.5, \
                                numpy.bitwise_and(bgr[:,:,0] >= 127.5, \
                                    numpy.bitwise_and(hsv[:,:,1] >= 49.5, yuv[:,:,1]<205.5) \
                                ) \
                            ) \
                        ) \
                    ) * 255)
        
    elif factor.General.cabin == 6:
        if useEmpty:
            emptyImg = emptiesTop[1]
        imageBinSeuil = numpy.uint8( \
                numpy.bitwise_or( \
                    numpy.bitwise_and( lab[:,:,1] >= 121.5, \
                        numpy.bitwise_or( \
                            numpy.bitwise_and( lab[:,:,2] < 146.5, \
                                numpy.bitwise_or( \
                                    numpy.bitwise_and( lab[:,:,1] >= 122.5, \
                                        numpy.bitwise_or( \
                                            numpy.bitwise_and( luv[:,:,1] >= 94.5, \
                                                numpy.bitwise_and( hsv[:,:,1] >= 38.5, \
                                                    numpy.bitwise_or( \
                                                        numpy.bitwise_and( lab[:,:,1] >= 124.5, \
                                                            numpy.bitwise_and( luv[:,:,2] >= 143.5, \
                                                                numpy.bitwise_and( hsv[:,:,1] >= 57.5, \
                                                                    numpy.bitwise_and( hsv[:,:,0] >= 22.5, yuv[:,:,2] < 116.5) \
                                                                ) \
                                                            ) \
                                                        ), \
                                                        numpy.bitwise_and(lab[:,:,1] < 124.5, \
                                                            numpy.bitwise_and( bgr[:,:,0] < 119.5, \
                                                                numpy.bitwise_or( \
                                                                    numpy.bitwise_and( hsv[:,:,1] < 47.5, \
                                                                        numpy.bitwise_and( lab[:,:,1] < 123.5, bgr[:,:,0] < 103.5) \
                                                                    ), \
                                                                    numpy.bitwise_and( hsv[:,:,1] >= 47.5, bgr[:,:,1] >= 56.5) \
                                                                ) \
                                                            ) \
                                                        ) \
                                                    ) \
                                                ) \
                                            ), \
                                            numpy.bitwise_and( luv[:,:,1] < 94.5, \
                                                numpy.bitwise_and( bgr[:,:,0] < 110.5, \
                                                    numpy.bitwise_and( lab[:,:,1] < 123.5, \
                                                        numpy.bitwise_or( numpy.bitwise_and( bgr[:,:,0] < 63.5, bgr[:,:,1] >= 56.5), \
                                                            numpy.bitwise_and( bgr[:,:,0] >= 63.5, \
                                                                numpy.bitwise_and(xyz[:,:,0] < 96.5, \
                                                                    numpy.bitwise_or( luv[:,:,2] >= 143.5, \
                                                                        numpy.bitwise_and( luv[:,:,2] < 143.5, \
                                                                            numpy.bitwise_and( luv[:,:,1] < 93.5, bgr[:,:,0] < 93.5) \
                                                                        ) \
                                                                    ) \
                                                                ) \
                                                            ) \
                                                        ) \
                                                    ) \
                                                ) \
                                            ) \
                                        ) \
                                    ), \
                                    numpy.bitwise_and( lab[:,:,1] < 122.5, \
                                        numpy.bitwise_or( \
                                            numpy.bitwise_and(bgr[:,:,0] >= 112.5, \
                                                numpy.bitwise_and(hsv[:,:,1] >= 48.5, bgr[:,:,0] < 130.5)\
                                            ), \
                                            numpy.bitwise_or(bgr[:,:,0] < 98.5, \
                                                numpy.bitwise_and( bgr[:,:,0] < 112.5, \
                                                    numpy.bitwise_or( hsv[:,:,1] >= 38.5, \
                                                        numpy.bitwise_and( hsv[:,:,1] < 38.5, \
                                                            numpy.bitwise_and( bgr[:,:,0] < 105.5, hsv[:,:,0] < 73.5) \
                                                        ) \
                                                    ) \
                                                ) \
                                            ) \
                                        ) \
                                    ) \
                                ) \
                            ), \
                            numpy.bitwise_and( lab[:,:,2] >= 146.5, bgr[:,:,0] < 161.5) \
                        ) \
                    ), \
                    numpy.bitwise_and( lab[:,:,1] < 121.5, \
                        numpy.bitwise_or( \
                            numpy.bitwise_and( bgr[:,:,0] >= 126.5, \
                                numpy.bitwise_and( hsv[:,:,1] >= 49.5, \
                                    numpy.bitwise_or( \
                                        numpy.bitwise_and( hsv[:,:,1] < 56.5, \
                                            numpy.bitwise_and( bgr[:,:,0] < 165.5, \
                                                numpy.bitwise_or( luv[:,:,2] >= 163.5, \
                                                    numpy.bitwise_and( luv[:,:,2] < 163.5, xyz[:,:,0] >= 157.5) \
                                                ) \
                                            ) \
                                        ), \
                                        numpy.bitwise_and( hsv[:,:,1] >= 56.5, bgr[:,:,0] < 169.5) \
                                    ) \
                                ) \
                            ), \
                            numpy.bitwise_or( bgr[:,:,0] < 108.5, \
                                numpy.bitwise_and( bgr[:,:,0] < 126.5, \
                                    numpy.bitwise_and( bgr[:,:,0] >= 108.5, \
                                        numpy.bitwise_or (hsv[:,:,1] >= 53.5, \
                                            numpy.bitwise_and( hsv[:,:,1] < 53.5, \
                                                numpy.bitwise_and( luv[:,:,2] >= 146.5, \
                                                    numpy.bitwise_or(bgr[:,:,0] < 116.5, \
                                                        numpy.bitwise_and( bgr[:,:,0] >= 116.5, hsv[:,:,1] >= 35.5) \
                                                    ) \
                                                ) \
                                            ) \
                                        ) \
                                    ) \
                                ) \
                            ) \
                        ) \
                    ) \
                ) * 255)
        
    else:
        imageBinSeuil = numpy.zeros(bgr.shape[0,2], 'uint8')
        emptyImg = numpy.zeros(bgr.shape, 'uint8')
        mask_pot = numpy.zeros(bgr.shape[0,2], 'uint8')
        mask_rails = numpy.zeros(bgr.shape[0,2], 'uint8')

    mask = numpy.bitwise_or(mask_pot, mask_rails)
    imageBinSeuilPot = numpy.bitwise_and(imageBinSeuil, mask)
    imageBinSeuilPot = ocv2.open(imageBinSeuilPot, iterations=3)

    if useEmpty:
        imageBinDiff = alinea.phenomenal.binarization_algorithm.mean_shift_binarization(bgr, emptyImg)*255
        imageBinDiff = numpy.bitwise_and(numpy.bitwise_and(imageBinDiff, imageBinSeuil), numpy.bitwise_not(mask))
    else:
        imageBinDiff = numpy.zeros(mask.shape, "uint8")

    return numpy.bitwise_or(imageBinSeuilPot, imageBinDiff)
