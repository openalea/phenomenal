# -*- python -*-
#
#       test_skeletonize_2d.py :
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

#       ========================================================================
#       Local Import
import alinea.phenomenal.skeletonize_2d as skeletonize_2d
import alinea.phenomenal.repair_processing as repair_processing
from phenomenal.test import tools_test

#       ========================================================================
#       Code


def test_skeletonize_2d():
    data_directory = "../../local/data/tests/Samples_binarization_2/"
    files = glob.glob(data_directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]), files)

    images = dict()
    for i in range(len(files)):
            images[angles[i]] = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)

    for angle in images:

        image_repair = repair_processing.fill_up_prop(images[angle])
        skeleton = skeletonize_2d.skeletonize_thinning(image_repair)

        tools_test.show_images([images[angle], skeleton])

        cv2.imwrite("../../local/data/refs/test_skeletonize/" +
                    "ref_skeletonize_%d.png" % angle, skeleton)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_skeletonize_2d()
