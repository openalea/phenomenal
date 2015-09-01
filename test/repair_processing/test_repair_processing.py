# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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
import glob

#       =======================================================================
#       Local Import 
from alinea.phenomenal import repair_processing
from phenomenal.test import tools_test

#       =======================================================================
#       Code


def test_repair_processing():

    data_directory = "../../local/data/tests/Samples_binarization_2/"
    files = glob.glob(data_directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(
                files[i], cv2.IMREAD_GRAYSCALE)

    for angle in images:
        image_repair = repair_processing.fill_up_prop(images[angle])

        tools_test.show_comparison_2_image(images[angle], image_repair)

        cv2.imwrite("../../local/data/refs/test_repair_processing/" +
                    "ref_repair_processing_%d.png" % angle, image_repair)

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_repair_processing()