# -*- python -*-
#
#       binarization_test_tools: Module Description
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
import sys
import numpy

#       =======================================================================

directories = [
    ['../../share/data/Samples_13_view/first/',
     '../../share/refs/test_binarization/Samples_13_view/first/'],

    ['../../share/data/Samples_13_view/last/',
     '../../share/refs/test_binarization/Samples_13_view/last/'],

    ['../../share/data/Samples_3_view/first/',
     '../../share/refs/test_binarization/Samples_3_view/first/'],

    ['../../share/data/Samples_3_view/last/',
     '../../share/refs/test_binarization/Samples_3_view/last/']]


def load_images(images_path):
    """
    Construct a list image from list image path

    :param images_path: A list containing the paths images.
    :return: A list containing the images
    """
    images = []
    for image_name in images_path:
        images.append(cv2.imread(image_name, cv2.CV_LOAD_IMAGE_UNCHANGED))

    return images


def print_check(string):
    sys.stdout.write('\n' + string + ' : ')
    sys.stdout.flush()


def check_result_with_ref(list_binarize_image,
                          refs_directory,
                          name_refs,
                          rewrite,
                          angles=None):

    refs_path = refs_directory + 'ref_' + name_refs + '_image_'

    # Transform binary image to grayscale
    for image in list_binarize_image:
        image[image == 1] = 255

    # Rewrite the refs binary image with the test image
    i = 0
    if rewrite:
        for image in list_binarize_image:
            if angles is not None:
                cv2.imwrite(refs_path + '%d.png' % angles[i], image)
            else:
                cv2.imwrite(refs_path + '%d.png' % i, image)
            i += 1

    i = 0
    # Test if the image refs is equals to image test
    for image in list_binarize_image:
        if angles is not None:
            ref_image = cv2.imread(refs_path + '%d.png' % angles[i],
                               cv2.CV_LOAD_IMAGE_GRAYSCALE)
        else:
            ref_image = cv2.imread(refs_path + '%d.png' % i,
                               cv2.CV_LOAD_IMAGE_GRAYSCALE)

        assert numpy.array_equal(ref_image, image)
        i += 1
