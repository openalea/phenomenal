# -*- python -*-
#
#       test_meanshift_binarization: Module Description
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
import glob

#       =======================================================================
#       Local Import
import alinea.phenomenal.binarization_algorithm as binarization_algorithm
import test_mean_image
import tools_test

#       =======================================================================


def check_mean_shift_binarization(data_directory,
                                  refs_directory,
                                  rewrite=False):
    """
    Test the function meanshift_binarization of alinea.phenomenal.binarization

    :param data_directory:
    :param refs_directory:
    :param rewrite:
    :return: None
    """
    images_path = glob.glob(data_directory + '*sv*.png')
    images = tools_test.load_images(images_path)
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]),
                 images_path)

    mean_image = test_mean_image.get_mean_image(images)

    list_binarize_image = []
    for image in images:
        list_binarize_image.append(
            binarization_algorithm.mean_shift_binarization(image, mean_image))

    tools_test.check_result_with_ref(list_binarize_image,
                                     refs_directory,
                                     "binarization_meanshift",
                                     rewrite,
                                     angles)


def test_suite_generator():
    tools_test.print_check(check_mean_shift_binarization.__name__)
    for directory in tools_test.directories:
        yield (check_mean_shift_binarization,
               directory[0],
               directory[1],
               True)

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    tools_test.print_check(check_mean_shift_binarization.__name__)
    for directory in tools_test.directories:
        check_mean_shift_binarization(directory[0], directory[1], True)
