# -*- python -*-
#
#       example_stack_image.py :
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
import alinea.phenomenal.result_viewer
import alinea.phenomenal.calibration_jerome
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation

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

            images_selected = dict()
            for angle in images:
                if 0 <= angle <= 360:
                    images_selected[angle] = images[angle]

            calibration = alinea.phenomenal.calibration_jerome.\
                Calibration.read_calibration(
                    calibration_name, file_is_in_share_directory=False)

            points_3d = alinea.phenomenal.multi_view_reconstruction.\
                reconstruction_3d(images_selected,
                                  calibration,
                                  precision=2,
                                  verbose=True)

            matrix = alinea.phenomenal.data_transformation.points_3d_to_matrix(
                points_3d, 2)

            alinea.phenomenal.data_transformation.save_matrix_like_stack_image(
                matrix,
                data_directory + 'stack_image_' + pot_id + '_' + date + '/')


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/fitted_result')
