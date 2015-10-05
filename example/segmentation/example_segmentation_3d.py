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
import glob
import os
import mayavi.mlab

from mayavi import mlab



#       ========================================================================
#       Local Import

from alinea.phenomenal.segmentation_3d import segment_organs_from_skeleton_3d
from alinea.phenomenal.reconstruction_3d_algorithm import Cube
from alinea.phenomenal.result_viewer import (plot_points_3d,
                                             plot_segments)

import alinea.phenomenal.misc
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

            example_segmentation_3d(points_3d, radius)

            # write_segmentation_3d(
            #     data_directory + 'segmentation_3d/',
            #     stem,
            #     leaves,
            #     cubes[0].radius)


def write_segmentation_3d(data_directory, file_name, stem, leaves, radius):
    directory = data_directory + 'segmentation_3d/'

    if not os.path.exists(directory):
        os.makedirs(directory)

    f = open(directory + file_name + '.xyz', 'w')

    f.write("%f\n" % (radius))
    stem_cubes = extract_points_3d(stem, radius)

    id = 0
    for cube in stem_cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f %d\n" % (x, y, z, id))
    id += 1

    for leaf in leaves:
        leaf_cubes = extract_points_3d(leaf, radius)
        for cube in leaf_cubes:
            x = cube.position[0, 0]
            y = cube.position[0, 1]
            z = cube.position[0, 2]

            f.write("%f %f %f %d\n" % (x, y, z, id))
        id += 1

    f.close()


def example_segmentation_3d(points_3d, radius):

    alinea.phenomenal.result_viewer.show_points_3d(
        points_3d, color=(0.1, 0.7, 0.1), scale_factor=10)

    #   ========================================================================

    skeleton_3d = alinea.phenomenal.skeletonize_3d. \
        skeletonize_3d_segment(points_3d, 10, 50)

    #   ========================================================================

    mayavi.mlab.figure("Skeleton")
    alinea.phenomenal.result_viewer.plot_vectors(skeleton_3d)
    alinea.phenomenal.result_viewer.plot_points_3d(
        points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
    mayavi.mlab.show()

    #   ========================================================================

    stem, leaves, segments = segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mlab.figure("Organs")
    for leaf in leaves:
        plot_segments(leaf.segments)
    plot_segments(stem.segments)
    plot_points_3d(points_3d, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    mlab.figure("Propagation")
    stem_points_3d = extract_points_3d(stem)
    color = plot_segments(stem.segments)
    plot_points_3d(stem_points_3d, color=color, scale_factor=3)

    for leaf in leaves:
        leaf_points_3d = extract_points_3d(leaf)
        color = plot_segments(leaf.segments)
        plot_points_3d(leaf_points_3d, color=color, scale_factor=3)

    # tools_test.plot_points_3d(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')
    # run_example('../../local/Figure_3D/')
