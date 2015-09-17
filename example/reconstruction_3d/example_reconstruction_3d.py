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
import cv2

#       ========================================================================
#       Local Import
from phenomenal.test.tools_test import show_cubes
from alinea.phenomenal.calibration_chessboard import Calibration
import alinea.phenomenal.reconstruction_3d as reconstruction_3d
#       ========================================================================
#       Code


def run_example(data_directory, calibration_name):

    pot_ids = load_files(data_directory + 'repair_processing/')

    for pot_id in pot_ids:
        for date in pot_ids[pot_id]:

            files = pot_ids[pot_id][date]

            images = load_images(files, cv2.IMREAD_UNCHANGED)

            calibration = Calibration.read_calibration(calibration_name)

            example_reconstruction_3d(images, calibration)


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
        if 0 <= angle <= 105:
            images_select[angle] = images[angle]

    cubes = reconstruction_3d.reconstruction_3d(images_select, calibration, 10)

    show_cubes(cubes, scale_factor=10)


def example_reconstruction_3d_manual(images)
#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    run_example('../../local/data_set_0962_A310_ARCH2013-05-13/',
                '../calibration/example_calibration_2')

