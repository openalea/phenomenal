# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import
import glob
import re
from mayavi import mlab
import re
import cv2


#       =======================================================================
#       Local Import
import alinea.phenomenal.configuration as configuration
import alinea.phenomenal.binarization as binarization
import alinea.phenomenal.repair_processing as repair_processing
import alinea.phenomenal.skeletonize_2d as skeletonize_2d
import alinea.phenomenal.skeletonize_3d as skeletonize_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.segmentation_3d as segmentation_3d
import phenomenal.test.tools_test as tools_test

#       =======================================================================
#       Code


def script_reconstruction_3d():
    # ==========================================================================
    # Select file images name

    data_directory = '../local/Figure_3D/'
    images_names = glob.glob(data_directory + '*sv*.png')

    id_plant = dict()
    for i in range(len(images_names)):

        number_pot = int(images_names[i].split('\\')[1].split('_')[0])
        angle = int(images_names[i].split('_sv')[1].split('.png')[0])

        if number_pot not in id_plant:
            id_plant[number_pot] = dict()

        images = id_plant[number_pot]
        images[angle] = images_names[i]

    for number_pot in id_plant:
        execute_script(id_plant[number_pot], str(number_pot))


def script_reconstruction_3d_2():
    data_directory = '../local/B73/'
    images_names = glob.glob(data_directory + '*sv*.png')

    id_plant = dict()
    for i in range(len(images_names)):
        date = images_names[i].split(' ')[0].split('_')[-1]
        angle = int(images_names[i].split('_sv')[1].split('.png')[0])

        if date not in id_plant:
            id_plant[date] = dict()

        images = id_plant[date]
        images[angle] = images_names[i]

    for date in id_plant:
        execute_script(id_plant[date], date)


def script_reconstruction_3d_595():
    # ==========================================================================
    # Select file images name

    data_directory = '../local/Figure_3D/'
    images_names = glob.glob(data_directory + '*sv*.png')

    id_plant = dict()
    for i in range(len(images_names)):

        number_pot = int(images_names[i].split('\\')[1].split('_')[0])
        angle = int(images_names[i].split('_sv')[1].split('.png')[0])

        if number_pot not in id_plant:
            id_plant[number_pot] = dict()

        images = id_plant[number_pot]
        images[angle] = images_names[i]


    execute_script(id_plant[595], str(595))



def execute_script(images_names, output_name):
    # ==========================================================================
    # Load images

    images = dict()
    for angle in images_names:
        images[angle] = cv2.imread(images_names[angle], cv2.IMREAD_UNCHANGED)

    # ==========================================================================
    # Load binarize configuration

    config = configuration.loadconfig('configuration_image_basic.cfg')
    binarization_configuration = configuration.binarization_config(config)

    # ==========================================================================
    # Binarize images

    mean_image = binarization.get_mean_image(images.values())

    images_binarize = dict()
    for angle in images:
        images_binarize[angle] = binarization.side_binarization(
            images[angle], mean_image, binarization_configuration)

    # ==========================================================================
    # Repair processing

    images_repair = dict()
    for angle in images_binarize:
        images_repair[angle] = repair_processing.fill_up_prop(
            images_binarize[angle])

    # ==========================================================================
    # Plot images

    # for angle in images:
    #     tools_test.show_images([images[angle], images_repair[angle]])

    # ==========================================================================
    # Load calibration for reconstruction 3d

    my_calibration = calibration_chessboard.Calibration.read_calibration(
        './calibration')

    # ==========================================================================
    # Select images for reconstruction

    images_for_reconstruction = dict()
    for angle in images_binarize:
        if angle < 210:
            images_for_reconstruction[angle] = images_repair[angle]

    # ==========================================================================
    # Compute reconstruction

    cubes_result = reconstruction_3d.reconstruction_3d(
        images_for_reconstruction, my_calibration, 5)

    # ==========================================================================
    # Plot reconstruction

    tools_test.show_cubes(cubes_result,
                          scale_factor=10,
                          figure_name=output_name)

    # ==========================================================================
    # Write reconstruction

    f = open(output_name + '.xyz', 'w')

    f.write("%f\n" % (cubes_result[0].radius))

    for cube in cubes_result:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f \n" % (x, y, z))

    f.close()

    # ==========================================================================
    # Plot cubes

    cubes = convert_orientation_cubes(cubes_result)

    mlab.figure("3D Reconstruction")
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=5)
    mlab.show()

    mlab.clf()
    mlab.close()

    # ==========================================================================
    # Plot cubes

    skeleton_3d = skeletonize_3d.skeletonize_3d_segment(cubes, 20, 25)

    #   ========================================================================

    mlab.figure("Skeleton")
    tools_test.plot_vectors(skeleton_3d)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    stem, leaves, segments = \
        segmentation_3d.segment_organs_from_skeleton_3d(skeleton_3d)

    #   ========================================================================

    mlab.figure("Organs")
    for leaf in leaves:
        tools_test.plot_segments(leaf.segments)
    tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()

    #   ========================================================================

    mlab.figure("Propagation")

    stem_cubes = give_cube(stem, cubes[0].radius)
    color = tools_test.plot_segments(stem.segments)
    tools_test.plot_cubes(stem_cubes, color=color, scale_factor=5)

    for leaf in leaves:
        leaf_cubes = give_cube(leaf, cubes[0].radius)
        color = tools_test.plot_segments(leaf.segments)
        tools_test.plot_cubes(leaf_cubes, color=color, scale_factor=5)

    # tools_test.plot_cubes(cubes, color=(0.1, 0.7, 0.1), scale_factor=3)
    mlab.show()


def convert_orientation_cubes(cubes):

    for cube in cubes:
        x = cube.position[0, 0]
        y = - cube.position[0, 2]
        z = - cube.position[0, 1]

        cube.position[0, 0] = x
        cube.position[0, 1] = y
        cube.position[0, 2] = z

    return cubes


def give_cube(organ, radius):
    cubes = list()

    for segment in organ.segments:
        for component in segment.component:
            for point in component:
                cube = reconstruction_3d.algo.Cube(point[0],
                                                   point[1],
                                                   point[2],
                                                   radius)

                cubes.append(cube)

    return cubes


def execute_script_2(images_names, output_name):
    # ==========================================================================
    # Load images

    images = dict()
    for angle in images_names:
        images[angle] = cv2.imread(images_names[angle], cv2.IMREAD_UNCHANGED)

    # ==========================================================================
    # Load binarize configuration

    config = configuration.loadconfig('configuration_image_basic.cfg')
    binarization_configuration = configuration.binarization_config(config)

    # ==========================================================================
    # Binarize images

    mean_image = binarization.get_mean_image(images.values())

    images_binarize = dict()
    for angle in images:
        images_binarize[angle] = binarization.side_binarization(
            images[angle], mean_image, binarization_configuration)

    # ==========================================================================
    # Repair processing

    images_repair = dict()
    for angle in images_binarize:
        images_repair[angle] = repair_processing.fill_up_prop(
            images_binarize[angle])

    # ==========================================================================
    # Plot images

    for angle in images:
         tools_test.show_images([images[angle], images_repair[angle]])


    # ==========================================================================
    # skeletonize

    skeletonize_images = list()
    for angle in images_repair:
        skeleton = skeletonize_2d.skeletonize_thinning(images_repair[angle])
        tools_test.show_image(skeleton, str(angle))


def read_xyz(directory='./'):
    # ==========================================================================
    # Read reconstruction
    xyz_files = glob.glob(directory + '*.xyz')

    for i in range(len(xyz_files)):

        read_cubes = list()
        with open(xyz_files[i], 'r') as f:

            radius = float(f.readline())
            for line in f:
                position = re.findall(r'[-0-9.]+', line)
                cube = reconstruction_3d.algo.Cube(position[0],
                                                   position[1],
                                                   position[2],
                                                   radius)

                read_cubes.append(cube)

        f.close()

        tools_test.show_cubes(read_cubes, figure_name=xyz_files[i])

#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    script_reconstruction_3d_595()
    # read_xyz()
