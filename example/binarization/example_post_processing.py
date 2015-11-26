# -*- python -*-
#
#       example_post_processing.py :
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
import os
import openalea.deploy.shared_data

#       ========================================================================
#       Local Import
import alinea.phenomenal
import alinea.phenomenal.binarization_post_processing
import alinea.phenomenal.viewer
import alinea.phenomenal.misc

#       ========================================================================
#       Code


def run_example(data_directory):
    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'binarization_mean_shift/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            share_data_directory = openalea.deploy.shared_data.\
                shared_data(alinea.phenomenal)

            mask_path = os.path.join(share_data_directory, 'roi_stem.png')
            mask_image = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

            post_processing_images = alinea.phenomenal.\
                binarization_post_processing.\
                remove_plant_support_from_images(images, mask=mask_image)

            # print pot_id, date
            # for angle in post_processing_images:
            #     alinea.phenomenal.viewer.show_images(
            #         [images[angle], post_processing_images[angle]], str(angle))

            alinea.phenomenal.misc.write_images(
                data_directory + 'post_processing_images/',
                files,
                post_processing_images)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
