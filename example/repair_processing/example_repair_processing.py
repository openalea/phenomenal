# -*- python -*-
#
#       example_repair_processing.py : 
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
#       ========================================================================
#       Local Import
from alinea.phenomenal.repair_processing import fill_up_prop
from alinea.phenomenal.result_viewer import show_images

from phenomenal.example.example_tools import \
    load_images, \
    load_files, \
    write_images

#       ========================================================================
#       Code


def run_example(data_directory):
    pot_ids = load_files(data_directory + 'binarization/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = load_images(files, cv2.IMREAD_UNCHANGED)

            repair_images = example_repair_processing(images)

            # print pot_id, date
            # for angle in repair_images:
            #     show_images([images[angle], repair_images[angle]],
            #                 str(angle))

            write_images(data_directory + 'repair_processing/',
                         files,
                         repair_images)


def example_repair_processing(images):

    repair_images = dict()
    for angle in images:
        if angle == -1:
            repair_images[angle] = fill_up_prop(images[angle],
                                                is_top_image=True)
        else:
            repair_images[angle] = fill_up_prop(images[angle])

    return repair_images

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')

    # run_example('../../local/Figure_3D/')