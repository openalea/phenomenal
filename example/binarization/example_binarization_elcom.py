# -*- python -*-
#
#       example_binarization_elcom.py :
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
import alinea.phenomenal.binarization
import alinea.phenomenal.configuration
import alinea.phenomenal.misc
import alinea.phenomenal.viewer

#       ========================================================================
#       Code


def run_example(data_directory):
    pot_ids = alinea.phenomenal.misc.load_files(data_directory)

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:
            files = pot_ids[pot_id][date]

            images = alinea.phenomenal.misc.load_images(
                files, cv2.IMREAD_UNCHANGED)

            images_elcom = dict()
            for angle in images:
                images_elcom[angle] = images[angle][0:2448, 0:2048]

            factor_binarization_elcom = alinea.phenomenal.configuration.\
                binarization_factor('factor_cubicle_6_elcom.cfg')

            images_binarize_elcom = alinea.phenomenal.binarization.binarization(
                images_elcom, factor_binarization_elcom, methods='elcom')

            # print pot_id, date
            # for angle in images:
            #     alinea.phenomenal.result_viewer.show_images([
            #         images[angle],
            #         images_binarize_elcom[angle]], str(angle))

            alinea.phenomenal.misc.write_images(
                data_directory + '/binarization_elcom/',
                files,
                images_binarize_elcom)




#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
