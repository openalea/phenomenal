# -*- python -*-
#
#       test_side_binarization: Module Description
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
import alinea.phenomenal.binarization as binarization
import alinea.phenomenal.configuration as configuration
import test_mean_image
import tools_test

#       =======================================================================

def check_side_binarization_meanshift(data_directory,
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
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]),
                 images_path)
    mean_image = test_mean_image.get_mean_image(images)

    config = configuration.loadconfig('configuration_image_basic.cfg')
    bin_config = configuration.binarization_config(config)

    list_binarize_image = []
    for image in images:
        list_binarize_image.append(
            binarization.side_binarization(image,
                                           mean_image,
                                           bin_config))

    tools_test.check_result_with_ref(list_binarize_image,
                                     refs_directory,
                                     "side_binarization_meanshift",
                                     rewrite,
                                     angles)


def test_suite_generator():
    tools_test.print_check(check_side_binarization_meanshift.__name__)
    for directory in tools_test.directories:
        yield (check_side_binarization_meanshift,
               directory[0],
               directory[1])

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    tools_test.print_check(check_side_binarization_meanshift.__name__)
    for directory in tools_test.directories:
        check_side_binarization_meanshift(directory[0], directory[1], True)