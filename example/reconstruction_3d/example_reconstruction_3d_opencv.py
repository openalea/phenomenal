# -*- python -*-
#
#       example_reconstruction_3d_opencv.py :
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
from alinea.phenomenal.result_viewer import show_cubes
from alinea.phenomenal.calibration_opencv import Calibration
from alinea.phenomenal.reconstruction_3d import reconstruction_3d
from phenomenal.example.example_tools import \
    load_files, \
    load_images, \
    write_cubes



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

            file_name = files[0].split('\\')[-1].split('_vis_')[0]
            write_cubes(cubes,
                        data_directory + 'reconstruction_3d/',
                        file_name)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/example_calibration_opencv')
    #
    # run_example('../../local/B73/',
    #             '../calibration/example_calibration_2')