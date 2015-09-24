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
from phenomenal.example.example_tools import load_files, load_images

from alinea.phenomenal.result_viewer import show_cubes
from alinea.phenomenal.reconstruction_3d import reconstruction_3d
from alinea.phenomenal.calibration_jerome import Calibration

#       ========================================================================
#       Code


def run_example(data_directory):

    pot_ids = load_files(data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            if len(files) > 3:
                images = load_images(files, cv2.IMREAD_UNCHANGED)

                selected_images = dict()
                for angle in images:
                    if 0 <= angle <= 360:
                        selected_images[angle] = images[angle]

                example_boostrap(selected_images)


def select_random_image(number_of_image, images):
    tmp_angles = list(images.keys())
    print tmp_angles
    selected_images = dict()

    for i in range(number_of_image):
        angle = random.choice(tmp_angles)
        tmp_angles.remove(angle)
        selected_images[angle] = images[angle]

    return selected_images


def example_boostrap(images):

    calibration = Calibration.read_calibration('../calibration/fitted_result')

    results_reconstruction_3d = list()
    for i in range(5):
        selected_images = select_random_image(5, images)

        cubes = reconstruction_3d(selected_images, calibration, precision=5)

        results_reconstruction_3d.append(cubes)

        print selected_images.keys()
        show_cubes(cubes, scale_factor=2)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')

    # run_example('../../local/Figure_3D/')
