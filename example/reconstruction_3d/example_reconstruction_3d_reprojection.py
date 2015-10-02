# -*- python -*-
#
#       example_reconstruction_3d_reprojection.py : 
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
import numpy as np

#       ========================================================================
#       Local Import
from alinea.phenomenal.misc import load_images, load_files
from alinea.phenomenal.result_viewer import show_cubes, show_images
from alinea.phenomenal.calibration_jerome import Calibration
from alinea.phenomenal.multi_view_reconstruction import reconstruction_3d
from alinea.phenomenal.reconstruction_3d_algorithm import bbox_projection

#       ========================================================================
#       Code


def run_example(data_directory, calibration_name):

    pot_ids = load_files(data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = load_images(files, cv2.IMREAD_UNCHANGED)

            calibration = Calibration.read_calibration(calibration_name)

            images_select = dict()
            for angle in images:
                if 0 <= angle <= 240:
                    images_select[angle] = images[angle]

            cubes = reconstruction_3d(images_select, calibration, precision=5)

            print pot_id, date
            show_cubes(cubes, scale_factor=5)

            for angle in images_select:

                img = images_select[angle].copy()
                h, l = np.shape(img)

                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

                for cube in cubes:
                    x_min, x_max, y_min, y_max = \
                        bbox_projection(cube, calibration, angle)

                    x_min = min(max(x_min, 0), l - 1)
                    x_max = min(max(x_max, 0), l - 1)
                    y_min = min(max(y_min, 0), h - 1)
                    y_max = min(max(y_max, 0), h - 1)

                    img[y_min:y_max + 1, x_min:x_max + 1] = [0, 0, 255]

                show_images([images_select[angle], img])


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/fitted_result')

    # run_example('../../local/B73/',
    #             '../calibration/example_calibration_2')
