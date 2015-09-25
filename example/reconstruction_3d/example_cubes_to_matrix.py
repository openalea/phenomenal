# -*- python -*-
#
#       example_cubes_to_matrix.py : 
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

from alinea.phenomenal.result_viewer import show_cubes, show_images
from alinea.phenomenal.misc import load_images, load_files
from alinea.phenomenal.calibration_jerome import Calibration
from alinea.phenomenal.reconstruction_3d import reconstruction_3d
from alinea.phenomenal.reconstruction_3d import (cubes_to_matrix,
                                                 save_matrix_like_stack_image)
from alinea.phenomenal.reconstruction_3d_algorithm import Cube

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

            rr = cubes[0].radius
            show_cubes(cubes, scale_factor=5)

            mat = cubes_to_matrix(cubes)

            cubes = list()
            for (x, y, z), value in np.ndenumerate(mat):
                if mat[x, y, z] == 1:
                    cube = Cube(x, y, z, rr)
                    cubes.append(cube)

            show_cubes(cubes, scale_factor=1)

            file_name = files[0].split('\\')[-1].split('_vis_')[0]
            save_matrix_like_stack_image(
                mat,
                data_directory + '/stack_images_' + file_name + '/')



#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/fitted_result')