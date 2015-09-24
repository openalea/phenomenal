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
import glob
from mayavi import mlab


#       ========================================================================
#       Local Import
from phenomenal.example.example_tools import read_xyz

from alinea.phenomenal.skeletonize_3d import skeletonize_3d_segment
from alinea.phenomenal.reconstruction_3d import change_orientation
from alinea.phenomenal.result_viewer import plot_vectors, plot_cubes

#       ========================================================================
#       Code

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

            example_skeletonize_3d(cubes)


            # print pot_id, date
            # for angle in skeleton_images:
            #     show_images([images[angle], skeleton_images[angle]],
            #                 str(angle))
            #
            # write_images(data_directory + 'skeletonize_2d/',
            #              files,
            #              skeleton_images)


def example_skeletonize_3d(cubes):

    #   ========================================================================

    # cubes = change_orientation(cubes)

    #   ========================================================================
    #
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
    #
    # #   ========================================================================
    #
    mlab.figure("Skeleton")
    plot_vectors(skeleton_3d)
    plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/')
    # run_example('../../local/B73/')

    # run_example('../../local/Figure_3D/')
