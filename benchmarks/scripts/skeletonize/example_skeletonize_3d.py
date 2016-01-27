# -*- python -*-
#
#       example_skeletonize_3d.py : 
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
import mayavi.mlab


#       ========================================================================
#       Local Import

import alinea.phenomenal.misc
import alinea.phenomenal.skeletonize_3d
import alinea.phenomenal.viewer


#       ========================================================================
#       Code


def run_example(data_directory):

    pot_ids = alinea.phenomenal.misc.load_xyz_files(
        data_directory + 'reconstruction_3d_model/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            xyz_file = pot_ids[pot_id][date]
            points_3d, radius = alinea.phenomenal.misc.read_xyz(xyz_file)

            alinea.phenomenal.viewer.show_points_3d(
                points_3d, color=(0.1, 0.7, 0.1), scale_factor=10)

            # alinea.phenomenal.skeletonize_3d.test_skeletonize_3d(
            #     points_3d, 10, 20)

            skeleton_3d = alinea.phenomenal.skeletonize_3d.\
                skeletonize_3d_segment(points_3d, 10, 50)

            mayavi.mlab.figure("Skeleton")
            alinea.phenomenal.viewer.plot_vectors(skeleton_3d)
            alinea.phenomenal.viewer.plot_points_3d(
                points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
            mayavi.mlab.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
