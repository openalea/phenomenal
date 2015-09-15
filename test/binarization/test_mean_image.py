# -*- python -*-
#
#       test_mean_image.py :
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
import glob
import numpy

#       ========================================================================
#       Local Import
import tools_test
import alinea.phenomenal.binarization as binarization

#       ========================================================================


def check_get_mean_image(data_directory, refs_directory, rewrite=False):
    """
     Test the function get_mean_image of this file
    """
    images_path = glob.glob(data_directory + '*sv*.png')
    images = tools_test.load_images(images_path)
    mean_image = binarization.get_mean_image(images)

    ref_mean_image = cv2.imread(refs_directory + 'ref_mean_image.png',
                                cv2.IMREAD_UNCHANGED)

    if rewrite:
        cv2.imwrite(refs_directory + 'ref_mean_image.png', mean_image)
    else:
        assert numpy.array_equal(ref_mean_image, mean_image)


def test_suite_generator():
    tools_test.print_check(check_get_mean_image.__name__)
    for directory in tools_test.directories:
        yield (check_get_mean_image, directory[0], directory[1])

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    tools_test.print_check(check_get_mean_image.__name__)
    for directory in tools_test.directories:
        check_get_mean_image(directory[0], directory[1], True)
