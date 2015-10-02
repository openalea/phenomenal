# -*- python -*-
#
#       example_boostrap.py : 
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
import random

#       ========================================================================
#       Local Import
import alinea.phenomenal.misc
import alinea.phenomenal.result_viewer
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.calibration_jerome

#       ========================================================================
#       Code


def run_example(data_directory):

    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            if len(files) > 3:
                images = alinea.phenomenal.misc.load_images(
                    files, cv2.IMREAD_UNCHANGED)

                selected_images = dict()
                for angle in images:
                    if 0 <= angle <= 360:
                        selected_images[angle] = images[angle]

                example_boostrap(selected_images)


def select_random_image(number_of_image, images):
    tmp_angles = list(images.keys())
    selected_images = dict()

    for i in range(number_of_image):
        angle = random.choice(tmp_angles)
        tmp_angles.remove(angle)
        selected_images[angle] = images[angle]

    return selected_images


def example_boostrap(images):

    calibration = alinea.phenomenal.calibration_jerome.Calibration.\
        read_calibration('../calibration/fitted_result',
                         file_is_in_share_directory=False)

    results_reconstruction_3d = list()
    for i in range(5):
        selected_images = select_random_image(5, images)

        points_3d = alinea.phenomenal.multi_view_reconstruction.\
            reconstruction_3d(selected_images, calibration, precision=4)

        results_reconstruction_3d.append(points_3d)

        print selected_images.keys()
        alinea.phenomenal.result_viewer.show_cubes(points_3d, scale_factor=2)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
