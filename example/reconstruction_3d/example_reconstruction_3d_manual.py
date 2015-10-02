# -*- python -*-
#
#       example_reconstruction_3d_manual.py : 
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
from alinea.phenomenal.misc import load_images, load_files, write_cubes
from alinea.phenomenal.result_viewer import show_cubes

import alinea.phenomenal.multi_view_reconstruction

from alinea.phenomenal.calibration_manual import Calibration

#       ========================================================================
#       Code

def run_example(data_directory):

    pot_ids = load_files(data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            images = load_images(files, cv2.IMREAD_UNCHANGED)

            calibration = Calibration()

            cubes = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
                images, calibration, precision=1)

            print pot_id, date
            show_cubes(cubes, scale_factor=1)

            file_name = files[0].split('\\')[-1].split('_vis_')[0]

            write_cubes(cubes,
                        data_directory + 'reconstruction_3d_manual/',
                        file_name)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')

    # run_example('../../local/Figure_3D/')
