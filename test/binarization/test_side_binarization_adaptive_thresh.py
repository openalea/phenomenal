# -*- python -*-
#
#       test_side_binarization_simon: Module Description
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
import cv2

#       =======================================================================
#       Local Import
import alinea.phenomenal.binarization as binarization
import alinea.phenomenal.configuration as configuration
import tools_test


#       =======================================================================

def check_side_binarization_adaptive_thresh(data_directory,
                                            refs_directory,
                                            rewrite=False):
    """
    :param data_directory:
    :param refs_directory:
    :param rewrite:
    :return:
    """

    images_path = glob.glob(data_directory + '*sv*.png')
    images = tools_test.load_images(images_path)
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), images_path)
    print images_path

    config = configuration.loadconfig('configuration_side_image_michael.cfg')
    bin_config = configuration.binarization_config(config)

    list_binarize_image = []
    for image in images:
        list_binarize_image.append(
            binarization.side_binarization_adaptive_thresh(image, bin_config))

    tools_test.check_result_with_ref(list_binarize_image,
                                     refs_directory,
                                     "side_binarization_adaptive_thresh",
                                     rewrite,
                                     angles)

check_side_binarization_adaptive_thresh(tools_test.directories[0][0],
               tools_test.directories[0][1],
               True)


def test_suite_generator():
    tools_test.print_check(check_side_binarization_adaptive_thresh.__name__)
    for directory in tools_test.directories:
        yield (check_side_binarization_adaptive_thresh,
               directory[0],
               directory[1],
               True)
