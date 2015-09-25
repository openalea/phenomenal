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
from mayavi import mlab


#       ========================================================================
#       Local Import

from alinea.phenomenal.misc import read_xyz
from alinea.phenomenal.skeletonize_3d import skeletonize_3d_segment
from alinea.phenomenal.segmentation_3d import segment_organs_from_skeleton_3d
from alinea.phenomenal.reconstruction_3d_algorithm import Cube
from alinea.phenomenal.result_viewer import (plot_vectors,
                                             plot_cubes,
                                             plot_segments)

#       ========================================================================
#       Code


def give_cube(organ, radius):
    cubes = list()

    for segment in organ.segments:
        for component in segment.component:
            for point in component:
                cube = Cube(point[0],
                            point[1],
                            point[2],
                            radius)

                cubes.append(cube)

    return cubes


def load_xyz_file(data_directory):
    images_names = glob.glob(data_directory + '*.xyz')

    pot_ids = dict()
    for i in range(len(images_names)):

        pot_id = images_names[i].split('\\')[-1].split('_')[0]
        if pot_id not in pot_ids:
            pot_ids[pot_id] = dict()

        date = images_names[i].split(' ')[0].split('_')[-1]

        pot_ids[pot_id][date] = images_names[i]

    return pot_ids


def run_example(data_directory):
    pot_ids = load_xyz_file(data_directory + 'reconstruction_3d_jerome/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            xyz_file = pot_ids[pot_id][date]
            cubes = read_xyz(xyz_file)

            example_segmentation_3d(cubes)

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
    stem_cubes = give_cube(stem, radius)

    id = 0
    for cube in stem_cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f %d\n" % (x, y, z, id))
    id += 1

    for leaf in leaves:
        leaf_cubes = give_cube(leaf, radius)
        for cube in leaf_cubes:
            x = cube.position[0, 0]
            y = cube.position[0, 1]
            z = cube.position[0, 2]

            f.write("%f %f %f %d\n" % (x, y, z, id))
        id += 1

    f.close()


def example_segmentation_3d(cubes):

    #   ========================================================================

    # cubes = change_orientation(cubes)

    #   ========================================================================

    mlab.figure("3D Reconstruction")
    plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=10)
    mlab.show()
    mlab.clf()
    mlab.close()

    #   ========================================================================

    # skeletonize.skeletonize_3d_transform_distance(opencv_cubes)

    # from alinea.phenomenal.skeletonize_3d import test_skeletonize_3d
    # test_skeletonize_3d(cubes, 10, 20)

    skeleton_3d = skeletonize_3d_segment(cubes, 10, 50)

    #   ========================================================================

    mlab.figure("Skeleton")
    plot_vectors(skeleton_3d)
    plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    stem, leaves, segments = segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mlab.figure("Organs")
    for leaf in leaves:
        plot_segments(leaf.segments)
    plot_segments(stem.segments)
    plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    mlab.figure("Propagation")

    stem_cubes = give_cube(stem, cubes[0].radius)
    color = plot_segments(stem.segments)
    plot_cubes(stem_cubes, color=color, scale_factor=3)

    for leaf in leaves:
        leaf_cubes = give_cube(leaf, cubes[0].radius)
        color = plot_segments(leaf.segments)
        plot_cubes(leaf_cubes, color=color, scale_factor=3)

    # tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')

    # run_example('../../local/Figure_3D/')
