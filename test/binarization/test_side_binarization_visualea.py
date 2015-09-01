# -*- python -*-
#
#       test_side_binarization_visualea: Module Description
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
import alinea.phenomenal.configuration as configuration
import tools_test
from openalea.core.alea import load_package_manager, function

#       =======================================================================

pm = load_package_manager()
node_factory = pm['alinea.phenomenal.macros']['side_binarisation']
side_binarization = function(node_factory)


def check_side_binarization_hsv(data_directory,
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

    config = configuration.getconfig(
        '../../share/data/config.cfg')

    obj = configuration.sidebinarisation_configuration(config)

    list_binarize_image = []
    for image in images:
        list_binarize_image.append(
            side_binarization(image, obj[0], obj[1], obj[2], obj[3])[0])

    tools_test.check_result_with_ref(list_binarize_image,
                                     refs_directory,
                                     "side_binarization_visualea_test",
                                     rewrite,
                                     angles)


def test_suite_generator():
    tools_test.print_check(check_side_binarization_hsv.__name__)
    for directory in tools_test.directories:
        yield (check_side_binarization_hsv,
               directory[0],
               directory[1])

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    tools_test.print_check(check_side_binarization_hsv.__name__)
    for directory in tools_test.directories:
        check_side_binarization_hsv(directory[0],
                                    directory[1],
                                    True)
