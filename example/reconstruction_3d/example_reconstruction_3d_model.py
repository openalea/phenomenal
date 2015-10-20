# -*- python -*-
#
#       example_reconstruction_3d_model.py :
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
import alinea.phenomenal.misc
import alinea.phenomenal.result_viewer
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.calibration_model


#       ========================================================================
#       Code


def run_example(data_directory, calibration_name):

    pot_ids = alinea.phenomenal.misc.load_files(
        data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            calibration = alinea.phenomenal.calibration_model.\
                Calibration.read_calibration(
                    calibration_name, file_is_in_share_directory=True)

            images_selected = dict()
            for angle in images:
                if 0 <= angle <= 360:
                    images_selected[angle] = images[angle]

            points_3d = alinea.phenomenal.multi_view_reconstruction. \
                reconstruction_3d(images_selected,
                                  calibration,
                                  precision=4,
                                  verbose=True)

            print pot_id, date
            alinea.phenomenal.result_viewer.show_points_3d(
                points_3d, scale_factor=2)

            file_name = files[0].split('\\')[-1].split('_vis_')[0]

            alinea.phenomenal.misc.write_points_3d(
                points_3d,
                4,
                data_directory + 'reconstruction_3d_model/',
                file_name)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                'fitted_result')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
