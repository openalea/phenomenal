# -*- python -*-
#
#       example_segmentation_3d.py : 
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
import alinea.phenomenal.segmentation_3d
import alinea.phenomenal.skeletonize_3d
import alinea.phenomenal.result_viewer

#       ========================================================================
#       Code


def extract_points_3d(organ):
    points_3d = list()

    for segment in organ.segments:
        for component in segment.component:
            for point in component:
                points_3d.append(point)

    return points_3d


def run_example(data_directory):

    pot_ids = alinea.phenomenal.misc.load_xyz_files(
        data_directory + 'reconstruction_3d_jerome/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            xyz_file = pot_ids[pot_id][date]
            points_3d, radius = alinea.phenomenal.misc.read_xyz(xyz_file)

            example_segmentation_3d(points_3d)


def example_segmentation_3d(points_3d):

    alinea.phenomenal.result_viewer.show_points_3d(
        points_3d, color=(0.1, 0.7, 0.1), scale_factor=10)

    #   ========================================================================

    skeleton_3d = alinea.phenomenal.skeletonize_3d.\
        skeletonize_3d_segment(points_3d, 10, 50)

    #   ========================================================================

    mayavi.mlab.figure("Skeleton")
    alinea.phenomenal.result_viewer.plot_vectors(skeleton_3d)
    alinea.phenomenal.result_viewer.plot_points_3d(
        points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
    mayavi.mlab.show()

    #   ========================================================================

    stem, leaves, segments = alinea.phenomenal.segmentation_3d.\
        segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mayavi.mlab.figure("Organs")
    for leaf in leaves:
        alinea.phenomenal.result_viewer.plot_segments(leaf.segments)
    alinea.phenomenal.result_viewer.plot_segments(stem.segments)
    alinea.phenomenal.result_viewer.plot_points_3d(
        points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
    mayavi.mlab.show()

    #   ========================================================================

    mayavi.mlab.figure("Propagation")
    stem_points_3d = extract_points_3d(stem)
    color = alinea.phenomenal.result_viewer.plot_segments(stem.segments)
    alinea.phenomenal.result_viewer.plot_points_3d(
        stem_points_3d, color=color, scale_factor=3)

    for leaf in leaves:
        leaf_points_3d = extract_points_3d(leaf)

        color = alinea.phenomenal.result_viewer.plot_segments(leaf.segments)

        alinea.phenomenal.result_viewer.plot_points_3d(
            leaf_points_3d, color=color, scale_factor=3)

    mayavi.mlab.show()
    mayavi.mlab.clf()
    mayavi.mlab.close()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    # run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
