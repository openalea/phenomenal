# -*- python -*-
#
#       example_reconstruction_3d.py : 
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
import re

import cv2






#       ========================================================================
#       Local Import
from phenomenal.test.tools_test import show_cubes
from alinea.phenomenal.calibration_chessboard import Calibration

import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import phenomenal.test.tools_test as tools_test

#       ========================================================================
#       Code

def read_xyz(file):
    # ==========================================================================
    # Read reconstruction

    read_cubes = list()
    with open(file, 'r') as f:

        radius = float(f.readline())
        for line in f:
            position = re.findall(r'[-0-9.]+', line)
            cube = reconstruction_3d.algo.Cube(position[0],
                                               position[1],
                                               position[2],
                                               radius)

            read_cubes.append(cube)

    f.close()

    tools_test.show_cubes(read_cubes, figure_name=file)


def write_cubes(cubes, data_directory, name_file):

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    f = open(data_directory + name_file + '.xyz', 'w')

    f.write("%f\n" % (cubes[0].radius))

    for cube in cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f \n" % (x, y, z))

    f.close()


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


def write_cubes_labelize(cubes, data_directory, name_file, id):
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    f = open(data_directory + name_file + '.xyz', 'w')

    f.write("%f\n" % (cubes[0].radius))

    for cube in cubes:
        x = cube.position[0, 0]
        y = cube.position[0, 1]
        z = cube.position[0, 2]

        f.write("%f %f %f %d\n" % (x, y, z, id))

    f.close()


def run_example(data_directory, calibration_name):

    pot_ids = load_files(data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            if len(files) > 3:
                images = load_images(files, cv2.IMREAD_UNCHANGED)

                calibration = Calibration.read_calibration(calibration_name)

                # import alinea.phenomenal.calibration_manual as cm
                # camera_config = cm.CameraConfiguration()
                # calibration = cm.Calibration(camera_config)

                cubes = example_reconstruction_3d(images, calibration)

                print pot_id, date
                show_cubes(cubes, scale_factor=3)

                file_name = files[0].split('\\')[-1].split('_vis_')[0]

                write_cubes(cubes,
                            data_directory + 'reconstruction_3/',
                            file_name)

                # cubes = convert_orientation_cubes(cubes)
                #
                # skeleton_3d = skeletonize_3d.skeletonize_3d_segment(cubes, 10, 20)
                #
                # stem, leaves, segments = \
                #     segmentation_3d.segment_organs_from_skeleton_3d(skeleton_3d)
                #
                # stem_cubes = give_cube(stem, cubes[0].radius)
                #
                # directory = data_directory + 'segmentation_3d/'
                #
                # if not os.path.exists(directory):
                #     os.makedirs(directory)
                #
                # f = open(directory + file_name + '.xyz', 'w')
                #
                # f.write("%f\n" % (cubes[0].radius))
                #
                # id = 0
                # for cube in stem_cubes:
                #     x = cube.position[0, 0]
                #     y = cube.position[0, 1]
                #     z = cube.position[0, 2]
                #
                #     f.write("%f %f %f %d\n" % (x, y, z, id))
                # id += 1
                #
                # for leaf in leaves:
                #     leaf_cubes = give_cube(leaf, cubes[0].radius)
                #     for cube in leaf_cubes:
                #         x = cube.position[0, 0]
                #         y = cube.position[0, 1]
                #         z = cube.position[0, 2]
                #
                #         f.write("%f %f %f %d\n" % (x, y, z, id))
                #     id += 1
                #
                # f.close()


def load_files(data_directory):

    images_names = glob.glob(data_directory + '*.png')

    pot_ids = dict()
    for i in range(len(images_names)):

        pot_id = images_names[i].split('\\')[-1].split('_')[0]
        if pot_id not in pot_ids:
            pot_ids[pot_id] = dict()

        date = images_names[i].split(' ')[0].split('_')[-1]
        if date not in pot_ids[pot_id]:
            pot_ids[pot_id][date] = dict()

        result = images_names[i].split('_sv')
        if len(result) == 2:
            angle = result[1].split('.png')[0]
        else:
            result = images_names[i].split('_tv')
            if len(result) == 2:
                angle = -1
            else:
                continue

        pot_ids[pot_id][date][int(angle)] = images_names[i]

    return pot_ids


def load_images(files, cv2_flag):
    images = dict()
    for angle in files:
        images[angle] = cv2.imread(files[angle], flags=cv2_flag)

    return images


def example_reconstruction_3d(images, calibration):

    #   ========================================================================

    images_select = dict()

    for angle in images:
        if 0 <= angle <= 240:
            images_select[angle] = images[angle]

    cubes = reconstruction_3d.reconstruction_3d(images_select,
                                                calibration,
                                                5)

    return cubes


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/example_calibration_2')

    # run_example('../../local/B73/',
    #             '../calibration/example_calibration_2')